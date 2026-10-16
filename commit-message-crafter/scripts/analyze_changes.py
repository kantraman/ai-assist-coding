#!/usr/bin/env python3
"""Analyse git changes to help write a good commit message.

Usage:
    analyze_changes.py                 # staged changes; falls back to working tree
    analyze_changes.py --unstaged      # force working-tree changes
    analyze_changes.py --commit REF    # a single existing commit
    analyze_changes.py --range A..B    # a range (for PR / squash messages)
    analyze_changes.py --json          # JSON output
    analyze_changes.py --repo PATH     # run against another directory

Stdlib only. Output is a set of hints and warnings, not a finished message.
"""
import argparse
import collections
import json
import os
import re
import subprocess
import sys

NOISE = re.compile(
    r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|Cargo\.lock|"
    r"Gemfile\.lock|composer\.lock|go\.sum|uv\.lock)$|\.snap$|\.min\.(js|css)$|(^|/)dist/|(^|/)build/"
)
DOC = re.compile(r"(\.(md|rst|txt|adoc)$)|(^|/)docs?/|(^|/)(README|CHANGELOG|LICENSE)", re.I)
TEST = re.compile(r"(^|/)(tests?|__tests__|spec)/|[._-](test|spec)\.\w+$|(^|/)test_\w+\.\w+$", re.I)
CI = re.compile(r"(^|/)\.github/|(^|/)\.gitlab-ci|(^|/)\.circleci/|Jenkinsfile|azure-pipelines", re.I)
BUILD = re.compile(
    r"(^|/)(package\.json|pyproject\.toml|setup\.(py|cfg)|requirements.*\.txt|Cargo\.toml|go\.mod|"
    r"pom\.xml|build\.gradle(\.kts)?|Gemfile|composer\.json|Dockerfile|docker-compose.*\.ya?ml|"
    r"Makefile|CMakeLists\.txt|webpack\.config\.\w+|vite\.config\.\w+|tsconfig.*\.json)$"
)
CONFIG = re.compile(r"(\.(ya?ml|toml|ini|cfg|conf|env\.example)$)|(^|/)\.[\w.-]*rc(\.\w+)?$")
MIGRATION = re.compile(r"(^|/)(migrations?|alembic|db/migrate)/|schema\.(sql|prisma|graphql)$|\.proto$|openapi.*\.(ya?ml|json)$", re.I)

SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "private key block"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"), "GitHub token"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "API secret key"),
    (re.compile(r"""(?i)\b(api[_-]?key|secret|passw(or)?d|token)\b\s*[:=]\s*['"][^'"\s]{8,}['"]"""), "hard-coded credential"),
]
DEBUG_PATTERNS = [
    (re.compile(r"\bconsole\.(log|debug)\("), "console.log"),
    (re.compile(r"^\s*debugger;?\s*$"), "debugger statement"),
    (re.compile(r"\b(pdb|ipdb)\.set_trace\(|^\s*breakpoint\(\)"), "Python breakpoint"),
    (re.compile(r"^\s*print\("), "print() call"),
    (re.compile(r"\b(TODO|FIXME|XXX|HACK)\b"), "TODO/FIXME marker"),
    (re.compile(r"\.only\("), "focused test (.only)"),
]
DEF_RE = re.compile(
    r"^\s*(?:export\s+(?:default\s+)?|public\s+|pub\s+)?(?:async\s+)?"
    r"(?:def|function|class|func|fn|interface|struct|enum|type)\s+([A-Za-z_]\w*)"
)
CONV_RE = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]+\))?!?: ")
TICKET_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
ISSUE_RE = re.compile(r"(?:^|[/_-])#?(\d{2,6})(?:[/_-]|$)")


def git(args, cwd, check=True):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, errors="replace")
    if check and r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "git failed: " + " ".join(args))
    return r.stdout


def diff_args(mode, ref):
    if mode == "staged":
        return ["--cached"]
    if mode == "unstaged":
        return []
    if mode == "commit":
        return [f"{ref}^!"]
    return [ref]  # range


def classify(path):
    if NOISE.search(path):
        return "generated"
    if CI.search(path):
        return "ci"
    if TEST.search(path):
        return "test"
    if BUILD.search(path):
        return "build"
    if DOC.search(path):
        return "docs"
    if MIGRATION.search(path):
        return "schema"
    if CONFIG.search(path):
        return "config"
    return "source"


def collect(cwd, mode, ref):
    base = diff_args(mode, ref)
    ns = git(["diff", "-M", "--name-status"] + base, cwd)
    nums = git(["diff", "-M", "--numstat"] + base, cwd)
    files = {}
    for line in ns.splitlines():
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R") or status.startswith("C"):
            path, old = parts[2], parts[1]
        else:
            path, old = parts[1], None
        files[path] = {"status": status[0], "old_path": old, "added": 0, "deleted": 0, "binary": False}
    for line in nums.splitlines():
        a, d, p = line.split("\t", 2)
        if "=>" in p:  # rename formatting like src/{a => b}/x.py
            m = re.match(r"(.*)\{(.*) => (.*)\}(.*)", p)
            p = (m.group(1) + m.group(3) + m.group(4)).replace("//", "/") if m else p.split(" => ")[-1]
        if p in files:
            if a == "-":
                files[p]["binary"] = True
            else:
                files[p]["added"], files[p]["deleted"] = int(a), int(d)
    patch = git(["diff", "-M", "-U0", "--no-color"] + base, cwd)
    return files, patch


def scan_patch(patch):
    """Return added/removed lines grouped by file."""
    cur, added, removed = None, collections.defaultdict(list), collections.defaultdict(list)
    for line in patch.splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:]
        elif line.startswith("+++ /dev/null"):
            cur = None
        elif line.startswith("--- a/") or line.startswith("--- /dev/null"):
            if line.startswith("--- a/"):
                cur = line[6:]
        elif cur and line.startswith("+") and not line.startswith("+++"):
            added[cur].append(line[1:])
        elif cur and line.startswith("-") and not line.startswith("---"):
            removed[cur].append(line[1:])
    return added, removed


def find_warnings(files, added, removed):
    warns = []
    for path, lines in added.items():
        kind = classify(path)
        if kind == "generated":
            continue
        for ln in lines:
            if ln.startswith(("<<<<<<<", ">>>>>>>")) or ln.strip() == "=======":
                warns.append({"level": "error", "file": path, "msg": "merge conflict marker"})
                break
        for rx, label in SECRET_PATTERNS:
            if any(rx.search(ln) for ln in lines):
                warns.append({"level": "error", "file": path, "msg": f"possible secret: {label}"})
                break
        if kind in ("source",):
            seen = set()
            for ln in lines:
                for rx, label in DEBUG_PATTERNS:
                    if rx.search(ln) and label not in seen:
                        seen.add(label)
                        warns.append({"level": "warn", "file": path, "msg": f"added {label}"})
    # removed definitions that don't reappear -> possibly breaking
    all_added = "\n".join("\n".join(v) for v in added.values())
    gone = []
    for path, lines in removed.items():
        if classify(path) != "source":
            continue
        for ln in lines:
            m = DEF_RE.match(ln)
            if m and not re.search(r"\b" + re.escape(m.group(1)) + r"\b", all_added):
                gone.append(f"{m.group(1)} ({path})")
    if gone:
        warns.append({"level": "info", "file": None,
                      "msg": "definitions removed and not re-added (possible breaking change): " + ", ".join(gone[:8])})
    for path, f in files.items():
        if classify(path) == "schema":
            warns.append({"level": "info", "file": path, "msg": "schema/migration/API contract touched; mention impact in body"})
    for path, f in files.items():
        if f["status"] == "D" and classify(path) == "source":
            warns.append({"level": "info", "file": path, "msg": "source file deleted"})
    return warns


def infer(files):
    meaningful = {p: f for p, f in files.items() if classify(p) != "generated"}
    cats = collections.Counter(classify(p) for p in meaningful)
    hints = []
    total = sum(cats.values())
    if not total:
        return cats, hints
    if cats.get("docs") == total:
        hints.append("docs: only documentation files changed")
    elif cats.get("test") == total:
        hints.append("test: only test files changed")
    elif cats.get("ci") == total:
        hints.append("ci: only CI/workflow files changed")
    elif cats.get("build", 0) + cats.get("config", 0) == total:
        hints.append("build/chore: only dependency, build or config files changed")
    else:
        src = [f for p, f in meaningful.items() if classify(p) == "source"]
        if src:
            new = sum(1 for f in src if f["status"] == "A")
            ren = sum(1 for f in src if f["status"] == "R")
            dele = sum(f["deleted"] for f in src)
            add = sum(f["added"] for f in src)
            if new and new >= len(src) / 2:
                hints.append("feat: new source files added")
            if ren and not add - dele > 20:
                hints.append("refactor: files renamed/moved with little new code")
            if src and abs(add - dele) <= max(3, 0.2 * max(add, dele)) and add > 5 and not new:
                hints.append("refactor or fix: roughly balanced adds/deletes in existing code")
            if add + dele <= 15 and not new and not ren:
                hints.append("fix: small targeted edit (verify against the diff; could also be tweak/chore)")
            if cats.get("test"):
                hints.append("tests changed alongside source: check whether tests encode a bug fix (fix) or new behaviour (feat)")
    return cats, hints


def scope_candidates(files):
    paths = [p for p in files if classify(p) == "source"] or \
            [p for p in files if classify(p) == "test"]
    if not paths:
        return []
    parts = [p.split("/") for p in paths]
    out = []
    # strip common container dirs
    skip = {"src", "lib", "app", "apps", "packages", "pkg", "internal", "cmd", "source"}
    def key(segs):
        segs = segs[:-1]
        for i, s in enumerate(segs):
            if s.lower() not in skip:
                return s
        return segs[-1] if segs else "(root)"
    counter = collections.Counter(key(s) for s in parts)
    for name, n in counter.most_common(3):
        if name != "(root)":
            out.append(f"{name} ({n} file{'s' if n != 1 else ''})")
    return out


def repo_style(cwd):
    try:
        subjects = git(["log", "-n", "40", "--no-merges", "--pretty=%s"], cwd).splitlines()
    except RuntimeError:
        return None
    if not subjects:
        return None
    n = len(subjects)
    conv = sum(1 for s in subjects if CONV_RE.match(s))
    ticket = sum(1 for s in subjects if TICKET_RE.search(s))
    lens = sorted(len(s) for s in subjects)
    past = sum(1 for s in subjects if re.match(r"^(\w+\([^)]*\):\s*|\w+:\s*)?(added|fixed|updated|removed|changed)\b", s, re.I))
    cap = sum(1 for s in subjects if re.match(r"^(\w+(\([^)]*\))?!?:\s*)?[A-Z]", s))
    types = collections.Counter(m.group(1) for s in subjects for m in [CONV_RE.match(s)] if m)
    verdict = "conventional-commits" if conv / n >= 0.5 else "plain-sentences"
    return {
        "samples": n,
        "style": verdict,
        "conventional_ratio": round(conv / n, 2),
        "ticket_prefix_ratio": round(ticket / n, 2),
        "median_subject_length": lens[n // 2],
        "past_tense_ratio": round(past / n, 2),
        "capitalised_ratio": round(cap / n, 2),
        "common_types": [t for t, _ in types.most_common(5)],
        "examples": subjects[:5],
    }


def branch_info(cwd):
    try:
        b = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd).strip()
    except RuntimeError:
        return {"branch": None}
    info = {"branch": b}
    m = TICKET_RE.search(b.upper()) if TICKET_RE.search(b.upper()) else None
    if m:
        info["ticket"] = m.group(1)
    else:
        m2 = ISSUE_RE.search(b)
        if m2:
            info["issue_number"] = m2.group(1)
    m3 = re.match(r"(feat|feature|fix|bugfix|hotfix|chore|docs|refactor|test|perf)[/_-]", b, re.I)
    if m3:
        info["branch_type_hint"] = m3.group(1).lower()
    return info


def analyse(cwd, mode, ref):
    note = None
    files, patch = collect(cwd, mode, ref)
    if mode == "staged" and not files:
        files, patch = collect(cwd, "unstaged", None)
        mode = "unstaged"
        note = "Nothing staged; showing working-tree changes instead."
    untracked = []
    if mode == "unstaged":
        untracked = [l for l in git(["ls-files", "--others", "--exclude-standard"], cwd).splitlines() if l]
    added, removed = scan_patch(patch)
    cats, hints = infer(files)
    total_add = sum(f["added"] for p, f in files.items() if classify(p) != "generated")
    total_del = sum(f["deleted"] for p, f in files.items() if classify(p) != "generated")
    warnings = find_warnings(files, added, removed)
    top_dirs = {p.split("/")[0] if "/" in p else "(root)" for p, f in files.items() if classify(p) in ("source", "test")}
    concerns = []
    if len(top_dirs) >= 4:
        concerns.append(f"touches {len(top_dirs)} separate top-level areas: {', '.join(sorted(top_dirs))}")
    nonnoise = [c for p in files for c in [classify(p)] if c != "generated"]
    has_src = "source" in nonnoise
    for extra in ("build", "ci", "config"):
        if has_src and extra in nonnoise and extra not in ("config",):
            concerns.append(f"{extra} changes mixed with source changes; consider separate commits")
    if total_add + total_del > 400:
        concerns.append(f"large change (+{total_add}/-{total_del}); check it is one logical unit")
    if untracked:
        concerns.append(f"{len(untracked)} untracked file(s) not included in the diff: {', '.join(untracked[:6])}")
    return {
        "mode": mode, "ref": ref, "note": note,
        "totals": {"files": len(files), "added": total_add, "deleted": total_del},
        "categories": dict(cats),
        "files": [{"path": p, **{k: v for k, v in f.items()}, "kind": classify(p)} for p, f in sorted(files.items())],
        "type_hints": hints,
        "scope_candidates": scope_candidates(files),
        "split_signals": concerns,
        "warnings": warnings,
        "repo_style": repo_style(cwd),
        "branch": branch_info(cwd),
    }


def render(r):
    L = []
    mode = {"staged": "staged changes", "unstaged": "working-tree changes",
            "commit": f"commit {r['ref']}", "range": f"range {r['ref']}"}[r["mode"]]
    L.append(f"== Analysis of {mode} ==")
    if r["note"]:
        L.append(f"NOTE: {r['note']}")
    t = r["totals"]
    L.append(f"{t['files']} file(s), +{t['added']} / -{t['deleted']} lines (generated/lock files excluded from line counts)")
    if not t["files"]:
        L.append("No changes found.")
        return "\n".join(L)
    L.append("")
    L.append("Files:")
    sym = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed", "C": "copied", "T": "type-changed"}
    for f in r["files"]:
        extra = f" (from {f['old_path']})" if f["old_path"] else ""
        sz = "binary" if f["binary"] else f"+{f['added']}/-{f['deleted']}"
        L.append(f"  [{f['kind']:<9}] {sym.get(f['status'], f['status']):<9} {f['path']}{extra}  {sz}")
    L.append("")
    if r["type_hints"]:
        L.append("Type hints (verify against the diff):")
        L += [f"  - {h}" for h in r["type_hints"]]
    if r["scope_candidates"]:
        L.append("Scope candidates: " + "; ".join(r["scope_candidates"]))
    b = r["branch"]
    bits = [f"{k}={v}" for k, v in b.items() if v]
    if bits:
        L.append("Branch: " + ", ".join(bits))
    if r["split_signals"]:
        L.append("")
        L.append("Consider splitting / check:")
        L += [f"  - {s}" for s in r["split_signals"]]
    if r["warnings"]:
        L.append("")
        L.append("Warnings:")
        icon = {"error": "ERROR", "warn": "warn ", "info": "info "}
        for w in r["warnings"]:
            where = f" [{w['file']}]" if w["file"] else ""
            L.append(f"  {icon[w['level']]}{where} {w['msg']}")
    s = r["repo_style"]
    if s:
        L.append("")
        L.append(f"Repo message style (last {s['samples']} non-merge commits):")
        L.append(f"  style: {s['style']} (conventional {int(s['conventional_ratio']*100)}%, "
                 f"ticket prefix {int(s['ticket_prefix_ratio']*100)}%)")
        L.append(f"  median subject length: {s['median_subject_length']} chars; "
                 f"capitalised {int(s['capitalised_ratio']*100)}%; past-tense {int(s['past_tense_ratio']*100)}%")
        if s["common_types"]:
            L.append("  common types: " + ", ".join(s["common_types"]))
        L.append("  recent subjects:")
        L += [f"    {x}" for x in s["examples"]]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--unstaged", action="store_true", help="analyse working-tree changes")
    g.add_argument("--commit", metavar="REF", help="analyse one existing commit")
    g.add_argument("--range", metavar="A..B", help="analyse a revision range")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--repo", default=".", help="path to the repository (default: cwd)")
    a = ap.parse_args()
    cwd = os.path.abspath(a.repo)
    try:
        git(["rev-parse", "--show-toplevel"], cwd)
    except (RuntimeError, FileNotFoundError):
        print("Not inside a git repository (or git is not installed).", file=sys.stderr)
        return 2
    mode, ref = ("commit", a.commit) if a.commit else ("range", a.range) if a.range else \
        ("unstaged", None) if a.unstaged else ("staged", None)
    try:
        r = analyse(cwd, mode, ref)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(r, indent=2) if a.json else render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
