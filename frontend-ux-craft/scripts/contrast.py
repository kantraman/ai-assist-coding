#!/usr/bin/env python3
"""WCAG contrast checker that understands hex AND oklch().

Usage:
  python contrast.py "#1a1a1a" "#ffffff"
  python contrast.py "oklch(24% 0.02 95)" "oklch(98.6% 0.006 95)"
  python contrast.py fg1 bg1 fg2 bg2 ...        # several pairs at once

Prints the ratio plus pass/fail for the thresholds that matter in practice:
  4.5  normal text (AA)      7    normal text (AAA)
  3.0  large text + UI parts (input borders, icons, focus rings)
Exit code is 1 if any pair is below 3:1.
"""
import math, re, sys


def _to_linear(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def parse(color: str):
    c = color.strip().lower()
    if c.startswith("#"):
        h = c[1:]
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        return [_to_linear(v) for v in (r, g, b)], False
    m = re.match(r"oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)(?:deg)?\s*(?:/.*)?\)", c)
    if not m:
        raise ValueError(f"Unsupported color: {color!r} (use #hex or oklch(L C H))")
    L = float(m.group(1)) / (100 if m.group(2) else 1)
    C, H = float(m.group(3)), math.radians(float(m.group(4)))
    a, b = C * math.cos(H), C * math.sin(H)
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    rgb = [
        4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
        -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
        -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_,
    ]
    out_of_gamut = any(v < -0.001 or v > 1.001 for v in rgb)
    return [min(1, max(0, v)) for v in rgb], out_of_gamut


def luminance(lin):
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(fg, bg):
    (f, fo), (b, bo) = parse(fg), parse(bg)
    l1, l2 = sorted((luminance(f), luminance(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05), fo or bo


def main(argv):
    if len(argv) < 2 or len(argv) % 2:
        print(__doc__)
        return 2
    below_floor = False
    for fg, bg in zip(argv[::2], argv[1::2]):
        r, oog = ratio(fg, bg)
        flags = (f"text AA {'PASS' if r >= 4.5 else 'fail'} | AAA {'PASS' if r >= 7 else 'fail'}"
                 f" | UI/large {'PASS' if r >= 3 else 'fail'}")
        note = "  (out of sRGB gamut; browsers will clip)" if oog else ""
        print(f"{r:5.2f}:1  {fg}  on  {bg}   {flags}{note}")
        below_floor |= r < 3
    return 1 if below_floor else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
