#!/usr/bin/env python3
"""Candidate generator for dead-code audits (stdlib only).

Finds: orphan files (no inbound imports), top-level symbols with no references,
symbols referenced only from tests, and unused third-party packages (Python/JS).
Output is a list of CANDIDATES with a confidence hint; a human/Claude must verify.

Usage: scan.py <repo-root> [--format md|json] [--min-lines N]
"""
import argparse, ast, json, os, re, subprocess, sys
from collections import defaultdict

PY, JS = {".py"}, {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
TEXT_EXT = PY | JS | {".json", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".md", ".html",
    ".sh", ".sql", ".txt", ".go", ".rs", ".java", ".kt", ".rb", ".php", ".cs", ".css", ".vue", ".svelte"}
SKIP_DIRS = {"node_modules", "vendor", "dist", "build", ".venv", "venv", "__pycache__", ".git", "third_party"}
ENTRY_NAMES = {"main", "__main__", "__init__", "conftest", "setup", "manage", "wsgi", "asgi",
    "index", "app", "server", "cli", "settings", "config"}
DYNAMIC_HINTS = re.compile(r"^\s*@\w+(\.\w+)+|@pytest\.fixture|@(task|shared_task)|"
    r"__all__|getattr\(|importlib|require\([^'\"]|import\(\s*[^'\"\s]|@Component|@Injectable|\bexport default\b", re.M)


def git(root, *args):
    try:
        return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=True).stdout
    except Exception:
        return None


def list_files(root):
    out = git(root, "ls-files")
    paths = out.splitlines() if out else [os.path.relpath(os.path.join(d, f), root)
        for d, ds, fs in os.walk(root) for f in fs if not set(d.split(os.sep)) & SKIP_DIRS]
    return [p for p in paths if not set(p.split("/")) & SKIP_DIRS]


def read(root, p):
    try:
        with open(os.path.join(root, p), encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def is_test(p):
    b = os.path.basename(p)
    return bool(re.search(r"(^|/)(tests?|__tests__|spec|e2e)(/|$)", p) or re.match(r"(test_.*|.*_test\.\w+|.*\.(test|spec)\.\w+)$", b))


def last_touched(root, p):
    out = git(root, "log", "-1", "--format=%cs", "--", p)
    return out.strip() if out else "n/a"


# ---------- import graph ----------
def py_module_names(p):
    parts = p[:-3].split("/")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return {".".join(parts[i:]) for i in range(len(parts))} if parts else set()


def py_imports(src):
    mods = set()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return mods
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom):
            base = ("." * n.level) + (n.module or "")
            mods.add(base)
            mods |= {f"{base}.{a.name}".lstrip(".") if n.level == 0 else f"{base}.{a.name}" for a in n.names}
    return mods


JS_IMPORT = re.compile(r"""(?:from\s+|import\s+|require\(\s*|import\(\s*)['"]([^'"]+)['"]""")


def resolve_js(root_files, frm, spec):
    if not spec.startswith("."):
        return None
    base = os.path.normpath(os.path.join(os.path.dirname(frm), spec)).replace(os.sep, "/")
    for cand in [base] + [base + e for e in JS] + [f"{base}/index{e}" for e in JS]:
        if cand in root_files:
            return cand
    return None


def resolve_py_relative(files, frm, mod):
    dots = len(mod) - len(mod.lstrip("."))
    pkg = os.path.dirname(frm).split("/") if os.path.dirname(frm) else []
    pkg = pkg[: len(pkg) - (dots - 1)] if dots > 1 else pkg
    rest = mod.lstrip(".").split(".") if mod.lstrip(".") else []
    base = "/".join(pkg + rest)
    for cand in (base + ".py", base + "/__init__.py"):
        if cand in files:
            return cand
    return None


def build_graph(root, files):
    fileset = set(files)
    by_mod = defaultdict(set)
    for p in files:
        if p.endswith(".py"):
            for m in py_module_names(p):
                by_mod[m].add(p)
    edges = defaultdict(set)  # target -> importers
    for p in files:
        ext = os.path.splitext(p)[1]
        src = read(root, p)
        if ext in PY:
            for m in py_imports(src):
                tgts = {resolve_py_relative(fileset, p, m)} if m.startswith(".") else by_mod.get(m, set())
                for t in tgts:
                    if t and t != p:
                        edges[t].add(p)
        elif ext in JS:
            for spec in JS_IMPORT.findall(src):
                t = resolve_js(fileset, p, spec)
                if t and t != p:
                    edges[t].add(p)
    return edges


def transitive_dependents(edges, target):
    seen, stack = set(), [target]
    while stack:
        for imp in edges.get(stack.pop(), ()):
            if imp not in seen:
                seen.add(imp)
                stack.append(imp)
    return seen


# ---------- symbols ----------
JS_SYM = re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function\*?|class|const|let|var)\s+([A-Za-z_$][\w$]*)", re.M)


def top_level_symbols(p, src):
    ext = os.path.splitext(p)[1]
    if ext in PY:
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return []
        return [(n.name, n.lineno, (n.end_lineno or n.lineno) - n.lineno + 1, bool(n.decorator_list)) for n in tree.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    if ext in JS:
        return [(m.group(1), src.count("\n", 0, m.start()) + 1, 1, False) for m in JS_SYM.finditer(src)]
    return []


def word_counts(contents, names):
    """Return {name: {path: occurrences}} using one pass per file."""
    pat = re.compile(r"\b(" + "|".join(re.escape(n) for n in names) + r")\b") if names else None
    res = defaultdict(lambda: defaultdict(int))
    if not pat:
        return res
    for p, src in contents.items():
        for m in pat.finditer(src):
            res[m.group(1)][p] += 1
    return res


# ---------- packages ----------
def unused_packages(root, files, contents):
    out = []
    if "package.json" in files:
        try:
            pj = json.loads(read(root, "package.json"))
        except ValueError:
            pj = {}
        code = "\n".join(s for p, s in contents.items() if os.path.splitext(p)[1] in JS)
        cfg = "\n".join(s for p, s in contents.items() if p != "package.json" and os.path.splitext(p)[1] not in JS)
        scripts = json.dumps(pj.get("scripts", {}))
        for sec in ("dependencies", "devDependencies"):
            for pkg in pj.get(sec, {}):
                if pkg.startswith("@types/"):
                    continue
                used = re.search(r"['\"]" + re.escape(pkg) + r"(/|['\"])", code)
                hinted = pkg in cfg or pkg.split("/")[-1] in scripts
                if not used:
                    out.append((pkg, sec, "low" if hinted or sec == "devDependencies" else "medium"))
    for f in files:
        if re.match(r"requirements.*\.txt$", os.path.basename(f)):
            imports = set()
            for p, s in contents.items():
                if p.endswith(".py"):
                    imports |= {m.split(".")[0].lower().replace("_", "-") for m in py_imports(s)}
            for line in read(root, f).splitlines():
                m = re.match(r"\s*([A-Za-z0-9_.\-]+)", line)
                if m and not line.strip().startswith(("#", "-")):
                    pkg = m.group(1).lower().replace("_", "-")
                    if pkg not in imports:
                        out.append((m.group(1), f, "low"))  # name!=import name is common
    return out


def commented_code_blocks(contents, min_lines=5):
    res = []
    for p, src in contents.items():
        ext = os.path.splitext(p)[1]
        if ext not in PY | JS:
            continue
        marker = "#" if ext in PY else "//"
        run, start = 0, 0
        codey = re.compile(r"[;{}()=]|\b(def|return|if|for|import|const|function)\b")
        for i, line in enumerate(src.splitlines() + [""], 1):
            s = line.strip()
            if s.startswith(marker) and codey.search(s[len(marker):]):
                if run == 0:
                    start = i
                run += 1
            else:
                if run >= min_lines:
                    res.append((p, start, run))
                run = 0
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--min-lines", type=int, default=5, help="min length of commented-out block to report")
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    files = [p for p in list_files(root) if os.path.splitext(p)[1] in TEXT_EXT]
    contents = {p: read(root, p) for p in files}
    code_files = [p for p in files if os.path.splitext(p)[1] in PY | JS]
    edges = build_graph(root, code_files)

    manifest_main = set()
    if "package.json" in contents:
        try:
            pj = json.loads(contents["package.json"])
            for k in ("main", "module", "types"):
                if isinstance(pj.get(k), str):
                    manifest_main.add(os.path.normpath(pj[k]).replace(os.sep, "/"))
            b = pj.get("bin")
            manifest_main |= {os.path.normpath(v) for v in (b.values() if isinstance(b, dict) else [b] if b else [])}
        except ValueError:
            pass

    orphans = []
    for p in code_files:
        stem = os.path.splitext(os.path.basename(p))[0]
        if edges.get(p) or is_test(p) or stem in ENTRY_NAMES or p in manifest_main:
            continue
        base_refs = sum(1 for q, s in contents.items() if q != p and re.search(r"\b" + re.escape(stem) + r"\b", s))
        conf = "high" if base_refs == 0 else "low"
        if DYNAMIC_HINTS.search(contents[p]):
            conf = "low" if conf == "high" else conf
        orphans.append({"file": p, "lines": contents[p].count("\n") + 1, "last_touched": last_touched(root, p),
                        "name_mentions_elsewhere": base_refs, "confidence": conf})

    orphan_files = {o["file"] for o in orphans if o["confidence"] == "high"}
    syms = {}
    for p in code_files:
        if p in orphan_files:  # already reported at file level
            continue
        for name, line, length, decorated in top_level_symbols(p, contents[p]):
            if not name.startswith("__"):
                syms[(p, name)] = (line, length, decorated)
    counts = word_counts(contents, sorted({n for _, n in syms}))
    unref, test_only = [], []
    for (p, name), (line, length, decorated) in syms.items():
        own = counts[name].get(p, 0)
        others = {q: c for q, c in counts[name].items() if q != p}
        prod_others = {q for q in others if not is_test(q)}
        if own > 1 or prod_others:  # used internally or elsewhere in production
            continue
        if is_test(p):
            continue
        rec = {"file": p, "symbol": name, "line": line, "lines": length}
        if not others and own <= 1:
            stem = os.path.splitext(os.path.basename(p))[0]
            rec["confidence"] = "medium" if DYNAMIC_HINTS.search(contents[p]) else "high"
            if os.path.splitext(p)[1] in JS and re.search(r"\bexport\b", contents[p]):
                rec["confidence"] = "medium"  # exported: may be public API
            if decorated or stem in ENTRY_NAMES or p in manifest_main:
                rec["confidence"] = "low"  # decorators register things; entry files are roots
                rec["why"] = "decorated (registry/route/task?)" if decorated else "lives in an entry/root file"
            unref.append(rec)
        elif others:
            rec["tests"] = sorted(others)[:3]
            rec["confidence"] = "medium"
            test_only.append(rec)

    result = {
        "root": root, "files_scanned": len(files),
        "orphan_files": sorted(orphans, key=lambda r: -r["lines"]),
        "unreferenced_symbols": sorted(unref, key=lambda r: (r["file"], r["line"])),
        "test_only_symbols": sorted(test_only, key=lambda r: (r["file"], r["line"])),
        "unused_packages": [{"package": n, "where": w, "confidence": c} for n, w, c in unused_packages(root, files, contents)],
        "commented_out_blocks": [{"file": f, "line": l, "lines": n} for f, l, n in commented_code_blocks(contents, a.min_lines)],
        "most_depended_on": [{"file": f, "dependents": len(transitive_dependents(edges, f))}
                             for f in sorted(edges, key=lambda k: -len(edges[k]))[:10]],
        "note": "Candidates only. Verify dynamic use (strings, config, reflection, framework conventions) before removing.",
    }
    if a.format == "json":
        print(json.dumps(result, indent=2))
        return
    o = [f"# Dead-code scan: {root}", f"Files scanned: {result['files_scanned']}", ""]
    o += ["## Orphan files (no inbound imports)", "| File | Lines | Last touched | Confidence |", "|---|---|---|---|"]
    o += [f"| {r['file']} | {r['lines']} | {r['last_touched']} | {r['confidence']} |" for r in result["orphan_files"]] or ["| none | | | |"]
    o += ["", "## Unreferenced top-level symbols", "| Symbol | File:line | Lines | Confidence |", "|---|---|---|---|"]
    o += [f"| {r['symbol']} | {r['file']}:{r['line']} | {r['lines']} | {r['confidence']} |" for r in result["unreferenced_symbols"]] or ["| none | | | |"]
    o += ["", "## Referenced only from tests", "| Symbol | File:line | Test refs |", "|---|---|---|"]
    o += [f"| {r['symbol']} | {r['file']}:{r['line']} | {', '.join(r['tests'])} |" for r in result["test_only_symbols"]] or ["| none | | |"]
    o += ["", "## Possibly unused packages"]
    o += [f"- {r['package']} ({r['where']}) [{r['confidence']}]" for r in result["unused_packages"]] or ["- none"]
    o += ["", "## Commented-out code blocks"]
    o += [f"- {r['file']}:{r['line']} ({r['lines']} lines)" for r in result["commented_out_blocks"]] or ["- none"]
    o += ["", "## Most depended-on files (transitive dependents)"]
    o += [f"- {r['file']}: {r['dependents']}" for r in result["most_depended_on"]] or ["- none"]
    o += ["", f"_{result['note']}_"]
    print("\n".join(o))


if __name__ == "__main__":
    main()
