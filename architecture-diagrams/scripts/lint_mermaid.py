#!/usr/bin/env python3
"""Static linter for Mermaid architecture diagrams.

Catches the mistakes that most often break rendering (especially in
LLM-generated Mermaid) without needing Node or a browser.

Usage:
    python lint_mermaid.py doc.md              # lint every ```mermaid block in a markdown file
    python lint_mermaid.py diagram.mmd         # lint a bare Mermaid file
    python lint_mermaid.py --render doc.md     # additionally try to render with mmdc if installed
    python lint_mermaid.py --max-nodes 8 doc.md

Exit code: 0 = no errors (warnings allowed), 1 = at least one error.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

VALID_TYPES = (
    "flowchart", "graph", "sequenceDiagram", "classDiagram",
    "stateDiagram-v2", "stateDiagram", "erDiagram",
)
DISCOURAGED_TYPES = (
    "C4Context", "C4Container", "C4Component", "C4Dynamic", "C4Deployment",
    "architecture-beta", "block-beta", "packet-beta", "kanban",
)
RESERVED_IDS = {"end", "graph", "subgraph", "style", "class", "classdef",
                "default", "click", "linkstyle", "direction", "flowchart"}

FENCE_RE = re.compile(r"```mermaid[ \t]*\n(.*?)```", re.S)


def extract_blocks(path):
    text = open(path, encoding="utf-8").read()
    if path.lower().endswith((".md", ".markdown")):
        blocks = []
        for m in FENCE_RE.finditer(text):
            line = text.count("\n", 0, m.start()) + 2  # first line inside fence
            blocks.append((line, m.group(1)))
        return blocks
    return [(1, text)]


def strip_comments(lines):
    return [l for l in lines if not l.strip().startswith("%%")]


def lint_block(code, max_nodes):
    errors, warns = [], []
    raw_lines = code.splitlines()
    lines = strip_comments(raw_lines)
    body = [l for l in lines if l.strip()]
    if not body:
        return ["empty diagram"], warns

    first = body[0].strip()
    kind = first.split()[0] if first.split() else ""

    if first.startswith("%%{"):
        warns.append("init directive %%{init}%% used: not portable across platforms")
        body_wo = [l for l in body if not l.strip().startswith("%%{")]
        first = body_wo[0].strip() if body_wo else ""
        kind = first.split()[0] if first else ""

    if kind in DISCOURAGED_TYPES:
        warns.append(f"'{kind}' is experimental / poorly supported; prefer flowchart-based C4 (see references/c4-in-mermaid.md)")
    elif kind not in VALID_TYPES:
        errors.append(f"first line must be a diagram type (flowchart, sequenceDiagram, classDiagram, stateDiagram-v2, erDiagram); got '{first[:40]}'")
        return errors, warns

    if kind == "graph":
        warns.append("use 'flowchart' instead of legacy 'graph'")
    if kind == "stateDiagram":
        warns.append("use 'stateDiagram-v2' instead of 'stateDiagram'")

    # ---- generic checks ----
    for i, l in enumerate(lines, 1):
        s = l.strip()
        if s.count('"') % 2 == 1:
            errors.append(f"line {i}: unbalanced double quotes: {s[:70]}")
        if "\\n" in s and "```" not in s:
            warns.append(f"line {i}: '\\n' in a label only breaks lines on newer Mermaid; use <br/> for portability")
        if re.search(r"fa:fa-|@\{\s*shape", s):
            warns.append(f"line {i}: icons / @{{shape}} syntax are not portable")
        if s.startswith("click "):
            warns.append(f"line {i}: 'click' is not supported on most platforms")
        if re.search(r"<(?!/?(br|b|i)\b|/?br)\w+[^>]*>", s) and not s.startswith("<<"):
            if kind in ("flowchart", "graph"):
                warns.append(f"line {i}: HTML other than <br/> and <b> may not render")

    if kind in ("flowchart", "graph"):
        lint_flowchart(lines, errors, warns, max_nodes)
    elif kind == "sequenceDiagram":
        lint_sequence(lines, errors, warns)
    elif kind == "classDiagram":
        lint_class(lines, errors, warns)
    elif kind == "erDiagram":
        lint_er(lines, errors, warns)
    return errors, warns


def lint_flowchart(lines, errors, warns, max_nodes):
    opens = ends = 0
    node_ids = set()
    node_def = re.compile(
        r'(?<![\w"])([A-Za-z_][\w\-]*)\s*(\[\[|\[\(|\(\[|\{\{|\[|\(\(|\(|\{)\s*(.*)')
    for i, l in enumerate(lines, 1):
        s = l.strip()
        if re.match(r"^subgraph\b", s):
            opens += 1
            m = re.match(r'^subgraph\s+(.*)$', s)
            rest = m.group(1).strip() if m else ""
            if rest.startswith('"'):
                warns.append(f"line {i}: prefer 'subgraph id [\"Title\"]' (id first) over a bare quoted title; edges to the subgraph need an id")
            idm = re.match(r"^([A-Za-z_][\w]*)", rest)
            if idm and idm.group(1).lower() in RESERVED_IDS - {"subgraph"}:
                errors.append(f"line {i}: subgraph id '{idm.group(1)}' is a reserved word")
            continue
        if s == "end":
            ends += 1
            continue
        if re.match(r"^(classDef|class|style|linkStyle|direction)\b", s):
            continue
        if re.match(r"^(flowchart|graph)(\s+(TB|TD|BT|RL|LR))?\s*$", s):
            continue

        # Unquoted labels containing risky characters (ignore edge labels |...|)
        s_nodes = re.sub(r"\|[^|]*\|", "||", s)
        for m in node_def.finditer(s_nodes):
            nid, shape, rest = m.group(1), m.group(2), m.group(3)
            node_ids.add(nid)
            if nid.lower() in RESERVED_IDS:
                errors.append(f"line {i}: node id '{nid}' is a reserved word; rename it (e.g. '{nid}Node')")
            if "-" in nid:
                warns.append(f"line {i}: node id '{nid}' contains a hyphen; works on current Mermaid but use camelCase for portability")
            inner = rest.lstrip()
            if not inner.startswith('"'):
                if re.search(r"[()\[\]{}]", inner.split("]")[0] if shape.startswith("[") else inner[:30]):
                    errors.append(f"line {i}: label for '{nid}' is not quoted but contains brackets/parentheses; wrap it in double quotes")

        # Edge labels with special characters but no quotes
        for m in re.finditer(r"\|([^|\"]*)\|", s):
            if re.search(r"[()\[\]{};]", m.group(1)):
                errors.append(f"line {i}: edge label contains special characters; quote it: |\"...\"|")

        # Unlabeled arrows are a quality issue, not a syntax error
        if re.search(r"(-->|-\.->|==>)\s*[A-Za-z_]", s) and not re.search(r"\|", s) and " & " not in s:
            if "-->|" not in s and "--" in s and not re.search(r'--\s*"', s):
                warns.append(f"line {i}: arrow has no label; label every arrow with a verb phrase")

        if re.search(r"(-->|---)[oOxX][A-Za-z]", s):
            warns.append(f"line {i}: '--o'/'--x' directly before an id is parsed as a circle/cross edge; add a space after the arrow")

    if opens != ends:
        errors.append(f"subgraph/end mismatch: {opens} subgraph vs {ends} end")

    # Count distinct nodes more robustly via edges
    edge_ids = set()
    for l in lines:
        for m in re.finditer(r"(?:^|[\s&>|])([A-Za-z_]\w*)(?=\s*(?:-->|---|-\.->|==>|\[|\(|\{|$|\s*&))", l):
            edge_ids.add(m.group(1))
    edge_ids -= {k for k in edge_ids if k.lower() in RESERVED_IDS}
    count = len(node_ids)
    if count > max_nodes:
        warns.append(f"{count} nodes (> {max_nodes}); consider splitting into focused diagrams")


def lint_sequence(lines, errors, warns):
    declared = set()
    stack = 0
    for i, l in enumerate(lines, 1):
        s = l.strip()
        m = re.match(r"^(?:participant|actor)\s+([A-Za-z_]\w*)", s)
        if m:
            declared.add(m.group(1))
        if re.match(r"^(alt|opt|loop|par|critical|break|rect)\b", s):
            stack += 1
        elif s == "end":
            stack -= 1
        if re.match(r"^(else|and|option)\b", s) and stack <= 0:
            errors.append(f"line {i}: '{s.split()[0]}' outside alt/par/critical block")
        m = re.match(r"^([A-Za-z_]\w*)\s*(-->>|->>|-\)|--\)|->|-->|-x|--x)[+\-]?\s*([A-Za-z_]\w*)\s*:(.*)$", s)
        if m:
            for pid in (m.group(1), m.group(3)):
                if declared and pid not in declared:
                    warns.append(f"line {i}: participant '{pid}' used but not declared; declare it so name and order are explicit")
            msg = m.group(4)
            if "#" in msg or ";" in msg:
                errors.append(f"line {i}: '#' truncates message text and ';' breaks parsing in sequence diagrams; reword")
    if stack != 0:
        errors.append(f"unbalanced alt/opt/loop/par blocks vs 'end' (off by {stack})")
    if len(declared) > 7:
        warns.append(f"{len(declared)} participants; consider splitting the flow")


def lint_class(lines, errors, warns):
    classes = 0
    for i, l in enumerate(lines, 1):
        s = l.strip()
        if re.match(r"^class\s+\w+", s):
            classes += 1
        if re.search(r"\w<\w[^>]*>", s) and "<<" not in s:
            warns.append(f"line {i}: generics with <> are fragile; use List~String~")
    if classes > 8:
        warns.append(f"{classes} classes; class diagrams are clearer with 8 or fewer")


def lint_er(lines, errors, warns):
    for i, l in enumerate(lines, 1):
        s = l.strip()
        m = re.match(r"^([A-Za-z_][\w\-]*)\s+[|}o][|o]--[|o][|{o]\s+([A-Za-z_][\w\-]*)\s*:\s*(.*)$", s)
        if m:
            for name in (m.group(1), m.group(2)):
                if "-" in name:
                    warns.append(f"line {i}: entity '{name}' contains a hyphen; use UPPER_SNAKE_CASE")
            label = m.group(3).strip()
            if " " in label and not label.startswith('"'):
                warns.append(f"line {i}: relationship label with spaces should be quoted")


def find_browser():
    """Return a Chrome/Chromium path: $MERMAID_BROWSER, then common locations."""
    env = os.environ.get("MERMAID_BROWSER")
    if env and os.path.exists(env):
        return env
    import glob
    patterns = [
        "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
        os.path.expanduser("~/.cache/puppeteer/chrome/*/chrome-linux64/chrome"),
        os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"),
        "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def try_render(code, label):
    mmdc = shutil.which("mmdc")
    if not mmdc:
        return None, "mmdc not installed; skipped render check"
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "in.mmd")
        out = os.path.join(d, "out.svg")
        open(src, "w", encoding="utf-8").write(code)
        cfg = os.path.join(d, "pp.json")
        import json
        pp = {"args": ["--no-sandbox"]}
        exe = find_browser()
        if exe:
            pp["executablePath"] = exe
        open(cfg, "w").write(json.dumps(pp))
        try:
            r = subprocess.run([mmdc, "-i", src, "-o", out, "-p", cfg],
                               capture_output=True, text=True, timeout=90)
        except subprocess.TimeoutExpired:
            return None, "mmdc timed out"
        if r.returncode == 0 and os.path.exists(out):
            return True, "renders OK"
        msg = (r.stderr or r.stdout).strip().splitlines()
        # Distinguish tooling problems from diagram problems
        joined = " ".join(msg)
        if "Could not find Chrome" in joined or "Failed to launch" in joined or "browser" in joined.lower():
            return None, "mmdc could not start a browser; render check skipped"
        return False, "render failed: " + " | ".join(msg[:3])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--render", action="store_true", help="also render each block with mmdc if available")
    ap.add_argument("--max-nodes", type=int, default=12)
    args = ap.parse_args()

    total_err = total_warn = total_blocks = 0
    for path in args.files:
        if not os.path.exists(path):
            print(f"{path}: file not found")
            total_err += 1
            continue
        blocks = extract_blocks(path)
        if not blocks:
            print(f"{path}: no mermaid blocks found")
            continue
        for idx, (line, code) in enumerate(blocks, 1):
            total_blocks += 1
            label = f"{path} [block {idx}, line {line}]"
            errors, warns = lint_block(code, args.max_nodes)
            if args.render:
                ok, msg = try_render(code, label)
                if ok is False:
                    errors.append(msg)
                elif ok is None:
                    warns.append(msg)
            status = "ERROR" if errors else ("warn" if warns else "ok")
            print(f"{label}: {status}")
            for e in errors:
                print(f"    error: {e}")
            for w in warns:
                print(f"    warn:  {w}")
            total_err += len(errors)
            total_warn += len(warns)

    print(f"\n{total_blocks} block(s), {total_err} error(s), {total_warn} warning(s)")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
