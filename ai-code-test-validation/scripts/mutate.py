#!/usr/bin/env python3
"""Lightweight, language-agnostic mutation check (fallback when PIT / Stryker /
mutmut / Stryker.NET cannot be installed).

For each mutable line in a source file, apply ONE small deliberate bug, run the
test command, and record whether the tests caught it (killed) or not (survived).
The original file is always restored, even on Ctrl-C or crash.

Usage:
  python mutate.py --file src/pricing.py --test-cmd "pytest -q" [--cwd .]
                   [--lines 10-40] [--build-cmd "dotnet build -nologo -v q"]
                   [--timeout 120] [--max 60]

Works for Python, JS/TS, Java, C#, Go, Rust and similar C-style languages.
--build-cmd: for compiled languages; a mutant that does not compile is marked
"invalid" and ignored (not counted as killed).
Exit code 0 = all valid mutants killed, 1 = survivors, 2 = baseline failed.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, tempfile

SKIP_PREFIXES = ("#", "//", "/*", "*", "import ", "from ", "using ", "package ",
                 "@", "use ", "#include", "'''", '"""')

# (name, compiled regex, replacement). Each match on a line yields one mutant.
OPS = [
    ("=== -> !==", re.compile(r"==="), "!=="),
    ("!== -> ===", re.compile(r"!=="), "==="),
    ("== -> !=", re.compile(r"(?<![=!<>])==(?!=)"), "!="),
    ("!= -> ==", re.compile(r"(?<![=!])!=(?!=)"), "=="),
    (">= -> >", re.compile(r">="), ">"),
    ("<= -> <", re.compile(r"<="), "<"),
    ("> -> >=", re.compile(r"(?<![-=>])>(?![=>])"), ">="),
    ("< -> <=", re.compile(r"(?<![<=])<(?![=<])"), "<="),
    ("&& -> ||", re.compile(r"&&"), "||"),
    ("|| -> &&", re.compile(r"\|\|"), "&&"),
    ("and -> or", re.compile(r"\band\b"), "or"),
    ("or -> and", re.compile(r"\bor\b"), "and"),
    ("+ -> -", re.compile(r"(?<=\s)\+(?=\s)"), "-"),
    ("- -> +", re.compile(r"(?<=\s)-(?=\s)"), "+"),
    ("* -> /", re.compile(r"(?<=\s)\*(?=\s)"), "/"),
    ("true -> false", re.compile(r"\btrue\b"), "false"),
    ("false -> true", re.compile(r"\bfalse\b"), "true"),
    ("True -> False", re.compile(r"\bTrue\b"), "False"),
    ("False -> True", re.compile(r"\bFalse\b"), "True"),
    ("int literal +1", re.compile(r"(?<![\w.])(\d+)(?![\w.])"), lambda m: str(int(m.group(1)) + 1)),
    ("not removed", re.compile(r"\bnot\s+"), ""),
    ("! removed", re.compile(r"!(?=[\w(])(?!=)"), ""),
]


def clear_stale_caches(path):
    """Python validates .pyc by (mtime in whole seconds, size). A same-size mutant
    written in the same second as the original would reuse a STALE compiled file,
    producing false survivors (or a corrupted baseline after restore). Delete them."""
    stem = os.path.splitext(os.path.basename(path))[0]
    for pyc in glob.glob(os.path.join(os.path.dirname(path), "__pycache__", stem + ".*.pyc")):
        try:
            os.remove(pyc)
        except OSError:
            pass


def write_source(path, text):
    """Write and bump mtime so incremental build tools (Maven/Gradle/dotnet/cargo)
    always see the file as changed."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    os.utime(path, None)
    clear_stale_caches(path)


def run(cmd, cwd, timeout):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True,
                           text=True, timeout=timeout, env=env)
        return p.returncode, (p.stdout + p.stderr)[-400:]
    except subprocess.TimeoutExpired:
        return "timeout", ""


def candidates(lines, lo, hi):
    in_block = False
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if "/*" in s and "*/" not in s:
            in_block = True
        if in_block:
            if "*/" in s:
                in_block = False
            continue
        if not s or s.startswith(SKIP_PREFIXES) or not (lo <= i <= hi):
            continue
        code = re.sub(r"(\"[^\"]*\"|'[^']*')", lambda m: "_" * len(m.group(0)), line)  # mask strings
        for name, rx, rep in OPS:
            for m in rx.finditer(code):
                new = rep(m) if callable(rep) else rep
                mutated = line[:m.start()] + new + line[m.end():]
                if mutated != line:
                    yield i, name, mutated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--test-cmd", required=True)
    ap.add_argument("--build-cmd")
    ap.add_argument("--cwd", default=".")
    ap.add_argument("--lines", default="1-999999")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--max", type=int, default=60)
    ap.add_argument("--json", dest="json_out")
    a = ap.parse_args()

    path = os.path.abspath(a.file)
    lo, hi = (int(x) for x in a.lines.split("-"))
    original = open(path, encoding="utf-8").read()
    lines = original.splitlines(keepends=True)
    backup = os.path.join(tempfile.mkdtemp(), os.path.basename(path))
    shutil.copy2(path, backup)

    clear_stale_caches(path)
    rc, out = run(a.test_cmd, a.cwd, a.timeout)
    if rc != 0:
        print("BASELINE FAILED: the suite must be green before mutating.\n" + out)
        sys.exit(2)

    cands = list(candidates(lines, lo, hi))
    if len(cands) > a.max:  # spread the sample evenly across the file
        step = len(cands) / a.max
        cands = [cands[int(k * step)] for k in range(a.max)]

    results = []
    try:
        for n, (ln, name, mutated) in enumerate(cands, 1):
            new_lines = lines[:]
            ending = "\n" if lines[ln - 1].endswith("\n") else ""
            new_lines[ln - 1] = mutated.rstrip("\n") + ending
            write_source(path, "".join(new_lines))
            status = None
            if a.build_cmd:
                brc, _ = run(a.build_cmd, a.cwd, a.timeout)
                if brc != 0:
                    status = "invalid"
            if status is None:
                trc, _ = run(a.test_cmd, a.cwd, a.timeout)
                status = "timeout" if trc == "timeout" else ("survived" if trc == 0 else "killed")
            results.append({"line": ln, "op": name, "status": status,
                            "before": lines[ln - 1].strip(), "after": mutated.strip()})
            print(f"[{n}/{len(cands)}] L{ln} {name}: {status}", flush=True)
    finally:
        write_source(path, original)  # ALWAYS restore (content + fresh mtime + no stale caches)

    valid = [r for r in results if r["status"] != "invalid"]
    killed = [r for r in valid if r["status"] in ("killed", "timeout")]
    surv = [r for r in valid if r["status"] == "survived"]
    score = 100 * len(killed) / len(valid) if valid else 100.0
    print(f"\nMutation score: {score:.0f}%  ({len(killed)} killed, {len(surv)} survived, "
          f"{len(results) - len(valid)} invalid)")
    if surv:
        print("\nSURVIVORS (each = a missing or weak test):")
        for r in surv:
            print(f"  L{r['line']} [{r['op']}]\n     - {r['before']}\n     + {r['after']}")
    if a.json_out:
        json.dump({"score": score, "results": results}, open(a.json_out, "w"), indent=2)
    restored = open(path, encoding="utf-8").read() == original
    prc, pout = run(a.test_cmd, a.cwd, a.timeout)
    print("\nOriginal file restored; post-run suite is green." if restored and prc == 0 else
          "\nWARNING: restore/post-run check FAILED. Verify the file and rebuild.\n" + pout)
    sys.exit(0 if not surv else 1)


if __name__ == "__main__":
    main()
