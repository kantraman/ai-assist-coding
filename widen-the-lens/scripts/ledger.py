#!/usr/bin/env python3
"""Attempt ledger: records debugging attempts and warns about repeats.

Usage:
  python ledger.py add "what I tried" --expected "..." --actual "..." [--verdict worked|no-change|worse|new-info]
  python ledger.py check "idea I am about to try"
  python ledger.py show
  python ledger.py reset

The ledger is stored in ./.attempt_ledger.json (override with LEDGER_FILE).
"""
import argparse, difflib, json, os, re, sys

PATH = os.environ.get("LEDGER_FILE", ".attempt_ledger.json")
THRESHOLD = 0.5  # similarity above this triggers a warning
# Words that carry no idea. "increase", "raise", "set" etc. are normalized below.
STOP = {"the", "a", "an", "to", "of", "and", "in", "on", "for", "it", "is", "try", "use", "again", "with"}
SYNONYMS = {
    "increase": "change", "raise": "change", "bump": "change", "lower": "change",
    "decrease": "change", "set": "change", "update": "change", "modify": "change",
    "adjust": "change", "edit": "change",
    "reboot": "restart", "relaunch": "restart", "reload": "restart",
}


def load():
    if os.path.exists(PATH):
        with open(PATH) as f:
            return json.load(f)
    return []


def save(items):
    with open(PATH, "w") as f:
        json.dump(items, f, indent=2)


def tokens(text):
    words = re.findall(r"[a-z]+|\d+[a-z]*", text.lower())
    # Drop pure numbers: "30s" vs "60s" should not make two ideas look different.
    words = [re.sub(r"^\d+[a-z]*$", "<num>", w) for w in words]
    words = [SYNONYMS.get(w, w) for w in words]
    return [w for w in words if w not in STOP]


def similarity(a, b):
    ta, tb = set(tokens(a)), set(tokens(b))
    jacc = len(ta & tb) / len(ta | tb) if ta | tb else 0.0
    seq = difflib.SequenceMatcher(None, " ".join(tokens(a)), " ".join(tokens(b))).ratio()
    return max(jacc, seq)


def similar(items, idea):
    hits = [(similarity(idea, it["idea"]), it) for it in items]
    return sorted([h for h in hits if h[0] >= THRESHOLD], key=lambda h: -h[0])


def report_repeats(items, idea):
    hits = similar(items, idea)
    for score, it in hits:
        print(f"WARNING: similar to attempt #{it['n']} ({score:.0%}): {it['idea']}")
        print(f"         result was: {it['verdict']} | {it['actual']}")
    if hits:
        print("Do not rerun the same idea. Pick a different hypothesis or widen the search.")
    return bool(hits)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("idea")
    a.add_argument("--expected", default="")
    a.add_argument("--actual", default="")
    a.add_argument("--verdict", default="no-change",
                   choices=["worked", "no-change", "worse", "new-info"])
    c = sub.add_parser("check")
    c.add_argument("idea")
    sub.add_parser("show")
    sub.add_parser("reset")
    args = p.parse_args()

    items = load()
    if args.cmd == "add":
        report_repeats(items, args.idea)
        n = len(items) + 1
        items.append({"n": n, "idea": args.idea, "expected": args.expected,
                      "actual": args.actual, "verdict": args.verdict})
        save(items)
        print(f"Recorded attempt #{n}.")
        failed = [i for i in items if i["verdict"] in ("no-change", "worse")]
        if len(failed) >= 3 and items[-1]["verdict"] != "worked":
            print("NOTE: 3+ failed attempts. Do the full reset (Step 7): restate facts, "
                  "flip your strongest assumption, shrink the problem.")
    elif args.cmd == "check":
        if not report_repeats(items, args.idea):
            print("No similar earlier attempt found. OK to proceed.")
    elif args.cmd == "show":
        if not items:
            print("Ledger is empty.")
        for it in items:
            print(f"#{it['n']} | idea: {it['idea']} | expected: {it['expected']} | "
                  f"actual: {it['actual']} | verdict: {it['verdict']}")
    elif args.cmd == "reset":
        save([])
        print("Ledger cleared.")


if __name__ == "__main__":
    sys.exit(main())
