#!/usr/bin/env python3
"""Find hardcoded color literals in a project.

Usage:
    python find_hardcoded_colors.py <dir> [--top N] [--detail] [--ignore NAME ...]

Counts hex (#rgb, #rgba, #rrggbb, #rrggbbaa), rgb()/rgba(), hsl()/hsla(),
and Flutter-style Color(0xAARRGGBB) literals per file. Skips common build and
dependency folders. Run it before and after theming work and compare totals.

Files that define tokens (theme/tokens/variables files) are expected to contain
literals; judge them separately from component files.
"""
import argparse
import os
import re
import sys
from collections import Counter

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", ".nuxt", "out", "coverage",
    "__pycache__", ".venv", "venv", "vendor", "Pods", ".dart_tool", ".gradle",
    "target", ".idea", ".vscode", ".backup",
}
EXTS = {
    ".css", ".scss", ".sass", ".less", ".styl", ".html", ".htm", ".vue", ".svelte",
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".json", ".dart", ".swift",
    ".kt", ".xml", ".java", ".svg", ".md", ".mdx", ".astro",
}

PATTERNS = [
    re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})\b"),
    re.compile(r"\brgba?\(\s*[^)]+\)", re.I),
    re.compile(r"\bhsla?\(\s*[^)]+\)", re.I),
    re.compile(r"\bColor\(\s*0x[0-9a-fA-F]{8}\s*\)"),
]
MAX_FILE_BYTES = 2_000_000


def scan_file(path):
    found = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, 1):
                for pat in PATTERNS:
                    for m in pat.finditer(line):
                        found.append((lineno, m.group(0)))
    except OSError:
        pass
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir")
    ap.add_argument("--top", type=int, default=15, help="how many files/colors to list")
    ap.add_argument("--detail", action="store_true", help="print every occurrence with line number")
    ap.add_argument("--ignore", nargs="*", default=[], help="extra directory names to skip")
    args = ap.parse_args()

    if not os.path.isdir(args.dir):
        print(f"Not a directory: {args.dir}")
        return 2

    skip = SKIP_DIRS | set(args.ignore)
    per_file = {}
    colors = Counter()

    for root, dirs, files in os.walk(args.dir):
        dirs[:] = [d for d in dirs if d not in skip]
        for name in files:
            if os.path.splitext(name)[1].lower() not in EXTS:
                continue
            path = os.path.join(root, name)
            try:
                if os.path.getsize(path) > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            hits = scan_file(path)
            if hits:
                per_file[path] = hits
                for _, c in hits:
                    colors[c.lower().replace(" ", "")] += 1

    total = sum(len(h) for h in per_file.values())
    print(f"Total color literals: {total}")
    print(f"Files with literals:  {len(per_file)}")
    print(f"Distinct values:      {len(colors)}")

    if per_file:
        print(f"\nTop {args.top} files:")
        ranked = sorted(per_file.items(), key=lambda kv: len(kv[1]), reverse=True)
        for path, hits in ranked[: args.top]:
            print(f"  {len(hits):5d}  {os.path.relpath(path, args.dir)}")

        print(f"\nTop {args.top} most repeated values:")
        for val, n in colors.most_common(args.top):
            print(f"  {n:5d}  {val}")

    if args.detail:
        print("\nAll occurrences:")
        for path, hits in sorted(per_file.items()):
            for lineno, val in hits:
                print(f"  {os.path.relpath(path, args.dir)}:{lineno}: {val}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
