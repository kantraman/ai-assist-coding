#!/usr/bin/env python3
"""WCAG contrast ratio checker.

Usage:
    python contrast.py <foreground> <background>
    python contrast.py "#111827" "#ffffff"
    python contrast.py 111827 fff

Accepts #rgb, #rrggbb (the # is optional). Prints the ratio and AA/AAA results.
Exit code 0 if normal-text AA (4.5:1) passes, 1 otherwise, so it can be used in checks.
"""
import sys


def parse_hex(value: str):
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        raise ValueError(f"Not a valid hex color: {value!r}")
    try:
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError(f"Not a valid hex color: {value!r}")


def channel(c: int) -> float:
    s = c / 255
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def luminance(rgb) -> float:
    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg: str, bg: str) -> float:
    l1, l2 = luminance(parse_hex(fg)), luminance(parse_hex(bg))
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    try:
        r = ratio(argv[1], argv[2])
    except ValueError as e:
        print(f"Error: {e}")
        return 2
    def mark(ok): return "PASS" if ok else "FAIL"
    print(f"Contrast {argv[1]} on {argv[2]}: {r:.2f}:1")
    print(f"  Normal text AA  (4.5:1): {mark(r >= 4.5)}")
    print(f"  Large text AA   (3.0:1): {mark(r >= 3.0)}")
    print(f"  UI parts/icons  (3.0:1): {mark(r >= 3.0)}")
    print(f"  Normal text AAA (7.0:1): {mark(r >= 7.0)}")
    return 0 if r >= 4.5 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
