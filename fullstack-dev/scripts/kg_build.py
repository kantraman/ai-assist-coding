#!/usr/bin/env python3
"""Knowledge-graph builder and validator for modular code (stdlib only).

Commands:
  validate  Check the graph against the ontology (exit 1 on errors; --strict also fails on warnings)
  impact    Show nodes affected by changing a node, and the tests to run
  stats     Fan-in / fan-out / instability per module
  mermaid   Print a Mermaid flowchart of the graph
  export    Print the merged graph as JSON
"""
import argparse
import json
import os
import sys
from collections import defaultdict, deque

SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv", ".next", "target"}
DEFAULT_ONTOLOGY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "ontology.json")
# Edges followed (in reverse) to find what a change can break.
IMPACT_RELS = {"depends_on", "consumes", "models", "persists", "exposes", "implements"}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def collect(root, manifest_name):
    nodes, edges, problems = {}, [], []
    found = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        if manifest_name not in filenames:
            continue
        found += 1
        path = os.path.join(dirpath, manifest_name)
        try:
            m = load_json(path)
        except Exception as e:  # noqa: BLE001
            problems.append(("error", f"{path}: invalid JSON ({e})"))
            continue
        decls = []
        if m.get("id"):
            main = {k: v for k, v in m.items() if k not in ("nodes", "edges")}
            main["type"] = main.get("type", "Module")
            decls.append(main)
        decls.extend(m.get("nodes", []))
        for d in decls:
            nid = d.get("id")
            if not nid or not d.get("type"):
                problems.append(("error", f"{path}: node missing id or type: {d}"))
                continue
            if nid in nodes:
                problems.append(("error", f"duplicate node id '{nid}' ({path} and {nodes[nid]['_src']})"))
                continue
            d = dict(d)
            d["_src"] = path
            nodes[nid] = d
        default_from = m.get("id")
        for e in m.get("edges", []):
            src = e.get("from", default_from)
            if not src or not e.get("rel") or not e.get("to"):
                problems.append(("error", f"{path}: malformed edge {e}"))
                continue
            edges.append({"from": src, "rel": e["rel"], "to": e["to"], "_src": path})
    if found == 0:
        problems.append(("error", f"no '{manifest_name}' files found under {root}"))
    return nodes, edges, problems


def find_cycles(nodes, edges, rels):
    adj = defaultdict(list)
    for e in edges:
        if e["rel"] in rels and e["from"] in nodes and e["to"] in nodes:
            adj[e["from"]].append(e["to"])
    index, low, on, stack, sccs, counter = {}, {}, set(), [], [], [0]

    def strong(v):
        # iterative Tarjan to avoid recursion limits
        work = [(v, iter(adj[v]))]
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        while work:
            node, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter[0]
                    counter[0] += 1
                    stack.append(w)
                    on.add(w)
                    work.append((w, iter(adj[w])))
                    advanced = True
                    break
                elif w in on:
                    low[node] = min(low[node], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                comp = []
                while True:
                    w = stack.pop()
                    on.discard(w)
                    comp.append(w)
                    if w == node:
                        break
                if len(comp) > 1 or node in adj[node]:
                    sccs.append(sorted(comp))

    for v in list(nodes):
        if v not in index:
            strong(v)
    return sccs


def validate(nodes, edges, onto):
    issues = []
    ntypes, etypes, layers = onto["node_types"], onto["edge_types"], onto["layers"]
    rules = onto.get("rules", {})
    for nid, n in nodes.items():
        spec = ntypes.get(n["type"])
        if spec is None:
            issues.append(("error", f"node '{nid}': unknown type '{n['type']}'"))
            continue
        for req in spec.get("requires", []):
            if req not in n:
                issues.append(("error", f"node '{nid}' ({n['type']}) missing required field '{req}'"))
        if "layer" in n and n["layer"] not in layers:
            issues.append(("error", f"node '{nid}': unknown layer '{n['layer']}'"))
    valid_edges = []
    for e in edges:
        spec = etypes.get(e["rel"])
        if spec is None:
            issues.append(("error", f"edge {e['from']} -{e['rel']}-> {e['to']}: unknown relation"))
            continue
        if e["from"] not in nodes:
            issues.append(("error", f"edge {e['rel']}: source '{e['from']}' is not a declared node ({e['_src']})"))
            continue
        if e["to"] not in nodes:
            issues.append(("error", f"dangling edge: {e['from']} -{e['rel']}-> '{e['to']}' (undeclared) ({e['_src']})"))
            continue
        ft, tt = nodes[e["from"]]["type"], nodes[e["to"]]["type"]
        if ft not in spec["from"] or tt not in spec["to"]:
            issues.append(("error", f"edge {e['from']}({ft}) -{e['rel']}-> {e['to']}({tt}) violates ontology"))
            continue
        valid_edges.append(e)
    # layering
    layered = rules.get("layered")
    if layered:
        for e in valid_edges:
            if e["rel"] != layered:
                continue
            a, b = nodes[e["from"]], nodes[e["to"]]
            la, lb = a.get("layer"), b.get("layer")
            if la in layers and lb in layers and layers[lb] > layers[la]:
                issues.append(("error", f"layer violation: {e['from']}[{la}] depends on {e['to']}[{lb}] (upward dependency)"))
    # cycles
    for rel in rules.get("acyclic", []):
        for comp in find_cycles(nodes, valid_edges, {rel}):
            issues.append(("error", f"cycle in '{rel}': {' -> '.join(comp)}"))
    # required edges
    out_rel, in_rel = defaultdict(set), defaultdict(set)
    for e in valid_edges:
        out_rel[e["from"]].add(e["rel"])
        in_rel[e["to"]].add(e["rel"])
    for r in rules.get("require_outgoing", []):
        for nid, n in nodes.items():
            if n["type"] == r["type"] and r["rel"] not in out_rel[nid]:
                issues.append((r.get("severity", "warn"), f"{n['type']} '{nid}' has no outgoing '{r['rel']}'"))
    for r in rules.get("require_incoming", []):
        for nid, n in nodes.items():
            if n["type"] == r["type"] and r["rel"] not in in_rel[nid]:
                issues.append((r.get("severity", "warn"), f"{n['type']} '{nid}' has no incoming '{r['rel']}'"))
    return issues, valid_edges


def impact(target, nodes, edges):
    if target not in nodes:
        return None
    rev = defaultdict(list)
    for e in edges:
        if e["rel"] == "exposes":
            # a module change flows forward to the endpoint it publishes
            rev[e["from"]].append(e["to"])
        elif e["rel"] in IMPACT_RELS:
            # a change to the target flows back to whatever depends on it
            rev[e["to"]].append(e["from"])
    seen, q = {target}, deque([target])
    while q:
        cur = q.popleft()
        for nxt in rev[cur]:
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    tests = set()
    tested = defaultdict(list)
    for e in edges:
        if e["rel"] == "tested_by":
            tested[e["from"]].append(e["to"])
    for nid in seen:
        tests.update(tested[nid])
    affected = sorted(seen - {target})
    return affected, sorted(tests)


def stats(nodes, edges):
    fin, fout = defaultdict(set), defaultdict(set)
    for e in edges:
        if e["rel"] == "depends_on":
            fout[e["from"]].add(e["to"])
            fin[e["to"]].add(e["from"])
    rows = []
    for nid, n in nodes.items():
        if n["type"] not in ("Module", "Component"):
            continue
        i, o = len(fin[nid]), len(fout[nid])
        inst = o / (i + o) if (i + o) else 0.0
        rows.append((nid, n.get("layer", "-"), i, o, round(inst, 2)))
    return sorted(rows, key=lambda r: (-r[2], r[0]))


def mermaid(nodes, edges):
    def safe(s):
        return "n_" + "".join(c if c.isalnum() else "_" for c in s)

    out = ["flowchart LR"]
    shapes = {"Module": ("[", "]"), "Requirement": ("([", "])"), "Endpoint": ("{{", "}}"),
              "Table": ("[(", ")]"), "Test": (">", "]"), "Entity": ("(", ")")}
    for nid, n in nodes.items():
        l, r = shapes.get(n["type"], ("[", "]"))
        label = nid.replace('"', "'")
        out.append(f'  {safe(nid)}{l}"{label}"{r}')
    for e in edges:
        if e["from"] in nodes and e["to"] in nodes:
            out.append(f"  {safe(e['from'])} -->|{e['rel']}| {safe(e['to'])}")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["validate", "impact", "stats", "mermaid", "export"])
    p.add_argument("target", nargs="?", help="node id (impact)")
    p.add_argument("--root", default=".", help="directory to scan for manifests")
    p.add_argument("--manifest", default="module.json", help="manifest file name")
    p.add_argument("--ontology", default=DEFAULT_ONTOLOGY)
    p.add_argument("--strict", action="store_true", help="treat warnings as failures")
    a = p.parse_args()

    onto = load_json(a.ontology)
    nodes, edges, problems = collect(a.root, a.manifest)
    issues, valid_edges = validate(nodes, edges, onto)
    issues = problems + issues

    if a.command == "validate":
        errs = [m for s, m in issues if s == "error"]
        warns = [m for s, m in issues if s == "warn"]
        for m in errs:
            print(f"ERROR   {m}")
        for m in warns:
            print(f"WARNING {m}")
        print(f"\n{len(nodes)} nodes, {len(valid_edges)} valid edges, {len(errs)} errors, {len(warns)} warnings")
        sys.exit(1 if errs or (a.strict and warns) else 0)
    if any(s == "error" for s, _ in issues) and a.command in ("impact", "stats"):
        print("note: graph has validation errors; results may be incomplete (run 'validate')", file=sys.stderr)
    if a.command == "impact":
        if not a.target:
            p.error("impact needs a node id")
        res = impact(a.target, nodes, valid_edges)
        if res is None:
            print(f"unknown node '{a.target}'", file=sys.stderr)
            sys.exit(2)
        affected, tests = res
        print(f"Change to '{a.target}' can affect {len(affected)} node(s):")
        for n in affected:
            print(f"  - {n} ({nodes[n]['type']})")
        print(f"Tests to run ({len(tests)}):")
        for t in tests:
            print(f"  - {t}")
    elif a.command == "stats":
        print(f"{'module':32} {'layer':8} {'fan-in':>6} {'fan-out':>7} {'instability':>11}")
        for nid, layer, i, o, inst in stats(nodes, valid_edges):
            print(f"{nid:32} {layer:8} {i:>6} {o:>7} {inst:>11}")
    elif a.command == "mermaid":
        print(mermaid(nodes, valid_edges))
    elif a.command == "export":
        clean = {k: {kk: vv for kk, vv in v.items() if kk != "_src"} for k, v in nodes.items()}
        print(json.dumps({"nodes": clean, "edges": [{k: v for k, v in e.items() if k != "_src"} for e in valid_edges]}, indent=2))


if __name__ == "__main__":
    main()
