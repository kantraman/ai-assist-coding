#!/usr/bin/env python3
"""Heuristic audit of an existing frontend project: design debt, a11y smells, security smells.

Usage:
  python audit_project.py <project-root> [--examples 4] [--json]

It reads source files only (css/scss/less/vue/svelte/jsx/tsx/js/ts/html/blade/php/twig/erb),
skipping node_modules, build output, vendor and VCS folders. Everything is regex-based, so treat
results as *leads to investigate*, not verdicts: multi-line tags are missed and some hits are
false positives. Its job is to turn "this UI feels inconsistent" into numbers you can shrink.
"""
import json, os, re, sys
from collections import Counter, defaultdict

SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", ".output", ".angular",
             ".svelte-kit", "vendor", "storage", "coverage", "__pycache__", ".cache", "out"}
SKIP_PATH_PARTS = ("public/build", "public/js", "public/css", ".min.")
EXTS = {".css", ".scss", ".sass", ".less", ".vue", ".svelte", ".jsx", ".tsx", ".js", ".ts",
        ".html", ".php", ".twig", ".erb", ".mjs", ".cjs"}
STYLE_EXTS = {".css", ".scss", ".sass", ".less", ".vue", ".svelte", ".html", ".jsx", ".tsx", ".ts", ".js"}

# --- token/value inventory (counted, not "flagged"): shows how many one-off values exist ---
INVENTORY = {
    "hex colors":       re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b"),
    "rgb/hsl colors":   re.compile(r"\b(?:rgba?|hsla?)\(\s*[\d.%\s,/-]+\)"),
    "font-size values": re.compile(r"font-size\s*:\s*([\d.]+(?:px|rem|em))"),
    "font families":    re.compile(r"font-family\s*:\s*([^;}{]+)"),
    "z-index values":   re.compile(r"z-index\s*:\s*(-?\d+)"),
    "border-radius":    re.compile(r"border-radius\s*:\s*([^;}{]+)"),
    "box-shadow":       re.compile(r"box-shadow\s*:\s*([^;}{]+)"),
    "breakpoints":      re.compile(r"@media[^{]*?\((?:min|max)-width\s*:\s*([\d.]+(?:px|em|rem))\)"),
}
# --- findings (each hit is a lead): (label, severity, regex, only_style_exts) ---
FINDINGS = [
    ("outline removed (check a :focus-visible replacement exists)", "a11y", re.compile(r"outline\s*:\s*(?:none|0)\b"), True),
    ("click handler on non-interactive element", "a11y", re.compile(r"<(?:div|span|li|p|td|section)\b[^>]*?(?:onClick=|@click|v-on:click|\(click\))"), False),
    ("<img> without alt (single-line tags)", "a11y", re.compile(r"<img\b(?![^>]*\balt\b)[^>]*>"), False),
    ("pinch-zoom disabled", "a11y", re.compile(r"user-scalable\s*=\s*(?:no|0)|maximum-scale\s*=\s*1(?:\.0)?\b"), False),
    ("positive tabindex", "a11y", re.compile(r"tabindex\s*=\s*[\"']?[1-9]"), False),
    ("font-size below 12px", "a11y", re.compile(r"font-size\s*:\s*(?:[0-9]|1[01])(?:\.\d+)?px"), True),
    ("placeholder used (verify a visible label exists too)", "a11y", re.compile(r"<input\b[^>]*\bplaceholder="), False),
    ("!important", "debt", re.compile(r"!important"), True),
    ("inline styles", "debt", re.compile(r"\bstyle\s*=\s*\"[^\"]+\"|style=\{\{|:style\s*=|\[ngStyle\]|\[style\.", re.I), False),
    ("deep selector escape hatches (::ng-deep, /deep/, :deep())", "debt", re.compile(r"::ng-deep|/deep/|:deep\("), True),
    ("HTML sink: dangerouslySetInnerHTML / v-html / {@html} / [innerHTML]", "security", re.compile(r"dangerouslySetInnerHTML|v-html|\{@html|\[innerHTML\]"), False),
    ("Angular sanitizer bypass", "security", re.compile(r"bypassSecurityTrust\w+"), False),
    ("DOM string injection: .innerHTML= / insertAdjacentHTML / document.write", "security", re.compile(r"\.innerHTML\s*=|\.outerHTML\s*=|insertAdjacentHTML|document\.write\("), False),
    ("eval / new Function", "security", re.compile(r"\beval\s*\(|new\s+Function\s*\("), False),
    ("target=_blank without rel (single-line tags)", "security", re.compile(r"<a\b(?![^>]*\brel\s*=)[^>]*target\s*=\s*[\"']_blank[\"'][^>]*>"), False),
    ("token/session-like value in web storage", "security", re.compile(r"(?:localStorage|sessionStorage)\.(?:set|get)Item\(\s*[\"'][^\"']*(?:token|jwt|auth|session|secret)[^\"']*[\"']", re.I), False),
    ("public env var with secret-looking name", "security", re.compile(r"(?:VITE|NEXT_PUBLIC|NG_APP|PUBLIC|NUXT_PUBLIC|MIX)_\w*(?:SECRET|PASSWORD|PRIVATE|TOKEN)\w*", re.I), False),
    ("hard-coded credential-looking string", "security", re.compile(r"(?:api[_-]?key|secret|passwd|password|token)\s*[:=]\s*[\"'][A-Za-z0-9_\-/+=]{12,}[\"']", re.I), False),
    ("postMessage with '*' target", "security", re.compile(r"postMessage\([^)]*[\"']\*[\"']\s*\)"), False),
]


def walk(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            p = os.path.join(dp, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext in EXTS and not any(part in p.replace("\\", "/") for part in SKIP_PATH_PARTS):
                yield p, ext


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__); return 2
    root = argv[0]
    n_ex = int(argv[argv.index("--examples") + 1]) if "--examples" in argv else 4
    as_json = "--json" in argv

    inv = {k: Counter() for k in INVENTORY}
    hits = defaultdict(list)
    css_vars_defined = css_vars_used = files = 0
    has_reduced_motion = has_focus_visible = has_dark = False
    motion_files = []

    for path, ext in walk(root):
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        files += 1
        rel = os.path.relpath(path, root)
        if ext in STYLE_EXTS:
            for name, rx in INVENTORY.items():
                for m in rx.finditer(text):
                    val = (m.group(1) if m.groups() else m.group(0)).strip().lower()
                    inv[name][re.sub(r"\s+", " ", val)] += 1
            css_vars_defined += len(re.findall(r"(?<![\w-])--[\w-]+\s*:", text))
            css_vars_used += len(re.findall(r"var\(\s*--", text))
            if re.search(r"prefers-reduced-motion", text): has_reduced_motion = True
            if re.search(r":focus-visible|focus-visible:", text): has_focus_visible = True
            if re.search(r"prefers-color-scheme|data-theme|\.dark\b|dark:|light-dark\(", text): has_dark = True
            if re.search(r"\b(?:transition|animation|@keyframes)\b", text): motion_files.append(rel)
        for label, sev, rx, style_only in FINDINGS:
            if style_only and ext not in STYLE_EXTS:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    hits[(sev, label)].append(f"{rel}:{i}: {line.strip()[:110]}")

    report = {
        "files_scanned": files,
        "inventory": {k: {"distinct": len(c), "total": sum(c.values()), "top": c.most_common(8)} for k, c in inv.items()},
        "custom_properties": {"defined": css_vars_defined, "var_usages": css_vars_used},
        "signals": {"has_reduced_motion_rule": has_reduced_motion, "has_focus_visible_rule": has_focus_visible,
                    "has_dark_mode_signal": has_dark, "files_with_motion": len(motion_files)},
        "findings": {f"{s}: {l}": {"count": len(v), "examples": v[:n_ex]} for (s, l), v in sorted(hits.items())},
    }
    if as_json:
        print(json.dumps(report, indent=2)); return 0

    print(f"\nAUDIT  {os.path.abspath(root)}   ({files} source files)\n" + "=" * 72)
    print("\nVALUE INVENTORY  (many distinct values = no system; goal is a handful, all tokenised)")
    for k, v in report["inventory"].items():
        if v["total"]:
            top = ", ".join(f"{val} ×{n}" for val, n in v["top"][:5])
            print(f"  {k:18s} {v['distinct']:4d} distinct / {v['total']:5d} uses   e.g. {top[:90]}")
    cp = report["custom_properties"]
    print(f"  {'CSS custom props':18s} {cp['defined']:4d} defined  / {cp['var_usages']:5d} var() uses"
          + ("   <- no token layer yet" if cp["defined"] < 10 else ""))
    print("\nBASELINE SIGNALS")
    for label, ok, want in [("prefers-reduced-motion handled", has_reduced_motion, motion_files),
                            (":focus-visible styles present", has_focus_visible, True),
                            ("dark mode / theming hook present", has_dark, True)]:
        note = "  (but %d files animate)" % len(motion_files) if (label.startswith("prefers") and not ok and motion_files) else ""
        print(f"  [{'x' if ok else ' '}] {label}{note}")
    print("\nFINDINGS  (leads to verify, grouped by kind)")
    for sev in ("security", "a11y", "debt"):
        block = [(l, v) for (s, l), v in sorted(hits.items()) if s == sev]
        if block:
            print(f"\n  [{sev.upper()}]")
            for label, v in block:
                print(f"    {len(v):4d}  {label}")
                for ex in v[:n_ex]:
                    print(f"          {ex}")
    if not hits:
        print("  none detected by these heuristics (does not mean none exist)")
    print("\nNext: use these numbers as the baseline. Re-run after each migration phase; they should fall.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
