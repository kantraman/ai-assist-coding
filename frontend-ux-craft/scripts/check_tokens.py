#!/usr/bin/env python3
"""Verify every text/UI pair in a light-dark() token file, in BOTH themes.

Usage:  python check_tokens.py assets/tokens.css
        python check_tokens.py path/to/your-tokens.css --set h-brand=155 --set h-neutral=70

Expects the token names used in assets/tokens.css (--text, --bg, --brand, ...).
Reports LOW (below WCAG threshold) and OOG (outside sRGB, browsers will clip and
the real ratio may differ). Exit code 1 if anything is reported.
"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contrast import ratio

PAIRS = [  # (foreground, background, minimum ratio)
    ("--text", "--bg", 4.5), ("--text", "--surface", 4.5), ("--text", "--surface-sunken", 4.5),
    ("--text-muted", "--bg", 4.5), ("--text-muted", "--surface", 4.5), ("--text-muted", "--surface-sunken", 4.5),
    ("--text-subtle", "--bg", 4.5), ("--text-subtle", "--surface", 4.5), ("--text-subtle", "--surface-sunken", 4.5),
    ("--border-strong", "--bg", 3), ("--border-strong", "--surface", 3), ("--border-strong", "--surface-sunken", 3),
    ("--on-brand", "--brand", 4.5), ("--on-brand", "--brand-hover", 4.5),
    ("--brand-text", "--bg", 4.5), ("--brand-text", "--surface", 4.5), ("--brand-text", "--brand-subtle", 4.5),
    ("--brand", "--bg", 3), ("--brand", "--surface", 3),
    ("--on-danger", "--danger", 4.5), ("--danger-text", "--bg", 4.5), ("--danger-text", "--danger-subtle", 4.5),
    ("--success-text", "--bg", 4.5), ("--success-text", "--success-subtle", 4.5),
    ("--warning-text", "--bg", 4.5), ("--warning-text", "--warning-subtle", 4.5),
    ("--info-text", "--bg", 4.5), ("--info-text", "--info-subtle", 4.5),
]
OK = r"(oklch\((?:[^()]|\([^)]*\))*\))"


def main(argv):
    if not argv:
        print(__doc__); return 2
    css = open(argv[0]).read()
    hues = {f"--{m[0]}": m[1] for m in re.findall(r"--(h-[\w-]+):\s*(\d+)", css)}
    for i, a in enumerate(argv):
        if a == "--set" and i + 1 < len(argv):
            k, v = argv[i + 1].split("=")
            hues[f"--{k}"] = v
    sub = lambda v: re.sub(r"var\((--h-[\w-]+)\)", lambda m: hues[m.group(1)], v)
    tok = {n: (sub(a), sub(b)) for n, a, b in
           re.findall(r"(--[\w-]+):\s*light-dark\(\s*" + OK + r",\s*" + OK + r"\s*\)", css)}
    missing = {t for p in PAIRS for t in p[:2]} - set(tok)
    if missing:
        print("Skipping (not defined as light-dark oklch tokens):", ", ".join(sorted(missing)))
    problems = 0
    for i, theme in enumerate(("light", "dark")):
        for fg, bg, need in PAIRS:
            if fg not in tok or bg not in tok:
                continue
            r, oog = ratio(tok[fg][i], tok[bg][i])
            if r < need or oog:
                problems += 1
                tag = ("LOW" if r < need else "") + (" OOG" if oog else "")
                print(f"[{theme}] {tag.strip():8s} {r:5.2f}:1 (need {need}) {fg} on {bg}")
    print(f"{len(tok)} tokens read, {problems} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
