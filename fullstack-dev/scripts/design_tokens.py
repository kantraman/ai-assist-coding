#!/usr/bin/env python3
"""Design tokens from one modular ratio, plus WCAG contrast checking (stdlib only).

  design_tokens.py --base 16 --ratio 1.25 --steps 6 > tokens.css
  design_tokens.py --ratio golden
  design_tokens.py --contrast "#1a1a1a" "#ffffff"
"""
import argparse
import re
import sys

GOLDEN = (1 + 5 ** 0.5) / 2


def lin(c):
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def parse_hex(h):
    h = h.strip().lstrip("#")
    if re.fullmatch(r"[0-9a-fA-F]{3}", h):
        h = "".join(ch * 2 for ch in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        sys.exit(f"invalid hex color: {h}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(rgb):
    r, g, b = (lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = luminance(parse_hex(a)), luminance(parse_hex(b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base", type=float, default=16, help="base font size in px")
    p.add_argument("--ratio", default="1.25", help="number or 'golden'")
    p.add_argument("--steps", type=int, default=6, help="steps above and below base")
    p.add_argument("--contrast", nargs=2, metavar=("FG", "BG"))
    a = p.parse_args()

    if a.contrast:
        r = contrast(*a.contrast)
        print(f"contrast ratio {r:.2f}:1")
        print(f"  normal text  AA {'pass' if r >= 4.5 else 'FAIL'} (4.5)   AAA {'pass' if r >= 7 else 'fail'} (7)")
        print(f"  large text   AA {'pass' if r >= 3 else 'FAIL'} (3)     AAA {'pass' if r >= 4.5 else 'fail'} (4.5)")
        print(f"  UI parts     AA {'pass' if r >= 3 else 'FAIL'} (3)")
        sys.exit(0 if r >= 4.5 else 1)

    ratio = GOLDEN if a.ratio == "golden" else float(a.ratio)
    if ratio <= 1:
        sys.exit("ratio must be > 1")
    out = [":root {", f"  /* modular scale: base {a.base:g}px, ratio {ratio:.3f} */"]
    names = {-2: "2xs", -1: "xs", 0: "base", 1: "md", 2: "lg", 3: "xl", 4: "2xl", 5: "3xl", 6: "4xl"}
    for n in range(-2, a.steps + 1):
        px = a.base * ratio ** n
        out.append(f"  --text-{names.get(n, n)}: {px / 16:.3f}rem; /* {px:.1f}px */")
    out.append("")
    out.append("  /* spacing: same ratio; whole px below base, 4px grid from base up */")
    for n in range(-3, 5):
        px = max(2, round(a.base * ratio ** n / 4) * 4) if n >= -1 else round(a.base * ratio ** n)
        out.append(f"  --space-{n + 4}: {px / 16:.3f}rem; /* {px}px */")
    out += ["",
            "  --leading-body: 1.5;", "  --leading-heading: 1.2;", "  --measure: 65ch;",
            f"  --radius-sm: {a.base * ratio ** -2 / 16:.3f}rem;",
            f"  --radius-md: {a.base * ratio ** -1 / 16:.3f}rem;",
            f"  --radius-lg: {a.base * ratio ** 0 / 16:.3f}rem;",
            "}"]
    print("\n".join(out))


if __name__ == "__main__":
    main()
