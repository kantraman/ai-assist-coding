#!/usr/bin/env python3
"""Generate a complete test report from JUnit XML (+ optional coverage).

Inputs
  --junit        glob(s) of JUnit XML files (pytest, jest-junit, Surefire, go-junit-report,
                 Playwright, Cypress, NUnit/xUnit junit loggers, ...)
  --coverage     Cobertura XML, JaCoCo XML, or lcov .info (optional)
  --previous     summary.json from an earlier run, for deltas (optional)
  --insights     Markdown file with analyst commentary, embedded at the top (optional)
  --repo         path to the git repo, to record commit / branch (optional)

Outputs  <out>.html, <out>.md, <out>.json (summary.json-compatible)

Stdlib only.
"""
import argparse
import datetime as dt
import glob
import html
import json
import os
import platform
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

TYPE_HINTS = [
    ("e2e", "e2e"), ("end-to-end", "e2e"), ("end2end", "e2e"), ("playwright", "e2e"), ("cypress", "e2e"),
    ("acceptance", "e2e"), ("integration", "integration"), ("it_", "integration"), ("api", "integration"),
    ("contract", "contract"), ("smoke", "smoke"), ("regression", "regression"),
    ("perf", "performance"), ("load", "performance"), ("security", "security"),
    ("component", "component"), ("unit", "unit"),
]


def infer_type(*texts):
    blob = " ".join(t.lower() for t in texts if t)
    for key, label in TYPE_HINTS:
        if key in blob:
            return label
    return "unit"


def parse_junit(path):
    """Yield test case dicts from one JUnit XML file."""
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        print(f"warning: could not parse {path}: {e}", file=sys.stderr)
        return []
    root = tree.getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    # avoid double-counting nested suites: only take suites that directly hold testcases
    cases = []
    src = os.path.basename(path)
    for suite in suites:
        suite_name = suite.get("name", "") or src
        for tc in suite.findall("testcase"):
            status, message, detail = "passed", "", ""
            flaky = False
            for child in tc:
                tag = child.tag
                if tag in ("failure", "error"):
                    status = "failed" if tag == "failure" else "error"
                    message = (child.get("message") or child.get("type") or "").strip()
                    detail = (child.text or "").strip()
                elif tag == "skipped":
                    if status == "passed":
                        status = "skipped"
                        message = (child.get("message") or "").strip()
                elif tag in ("flakyFailure", "flakyError", "rerunFailure", "rerunError"):
                    flaky = True
                    if not message:
                        message = (child.get("message") or "").strip()
            try:
                secs = float(tc.get("time") or 0)
            except ValueError:
                secs = 0.0
            classname = tc.get("classname") or ""
            cases.append({
                "id": f"{classname}::{tc.get('name', '')}".strip(":"),
                "name": tc.get("name", ""),
                "classname": classname,
                "suite": suite_name,
                "file": tc.get("file") or tc.get("filepath") or "",
                "status": status,
                "flaky": flaky,
                "time": secs,
                "message": message,
                "detail": detail,
                "type": infer_type(src, suite_name, classname, tc.get("file") or ""),
                "source": src,
            })
    return cases


def pct(n, d):
    return round(100.0 * n / d, 2) if d else 0.0


def parse_coverage(path):
    """Return {"tool": str, "line_pct": float, "branch_pct": float|None, "files": [{file, pct}]}"""
    if not path or not os.path.exists(path):
        return None
    if path.endswith((".info", ".lcov")) or os.path.basename(path).startswith("lcov"):
        files, cur = {}, None
        for line in open(path, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if line.startswith("SF:"):
                cur = line[3:]
                files[cur] = {"lf": 0, "lh": 0, "bf": 0, "bh": 0}
            elif cur and line.startswith("LF:"):
                files[cur]["lf"] = int(line[3:])
            elif cur and line.startswith("LH:"):
                files[cur]["lh"] = int(line[3:])
            elif cur and line.startswith("BRF:"):
                files[cur]["bf"] = int(line[4:])
            elif cur and line.startswith("BRH:"):
                files[cur]["bh"] = int(line[4:])
        lf = sum(f["lf"] for f in files.values())
        lh = sum(f["lh"] for f in files.values())
        bf = sum(f["bf"] for f in files.values())
        bh = sum(f["bh"] for f in files.values())
        return {"tool": "lcov", "line_pct": pct(lh, lf), "branch_pct": pct(bh, bf) if bf else None,
                "files": [{"file": k, "pct": pct(v["lh"], v["lf"]), "lines": v["lf"]} for k, v in files.items()]}
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        print(f"warning: could not parse coverage {path}: {e}", file=sys.stderr)
        return None
    if root.tag == "coverage":  # Cobertura
        files = {}
        for cls in root.iter("class"):
            fn = cls.get("filename", "")
            lines = cls.findall("./lines/line")
            tot = len(lines)
            hit = sum(1 for l in lines if int(l.get("hits", "0")) > 0)
            cur = files.setdefault(fn, [0, 0])
            cur[0] += tot
            cur[1] += hit
        lr = root.get("line-rate")
        br = root.get("branch-rate")
        total = sum(v[0] for v in files.values())
        hits = sum(v[1] for v in files.values())
        line_pct = round(float(lr) * 100, 2) if lr not in (None, "") and total == 0 else pct(hits, total)
        branch_pct = round(float(br) * 100, 2) if br not in (None, "", "0") else None
        return {"tool": "cobertura", "line_pct": line_pct, "branch_pct": branch_pct,
                "files": [{"file": k, "pct": pct(v[1], v[0]), "lines": v[0]} for k, v in files.items()]}
    if root.tag == "report":  # JaCoCo
        def counter(el, kind):
            for c in el.findall("counter"):
                if c.get("type") == kind:
                    return int(c.get("missed")), int(c.get("covered"))
            return None
        lc = counter(root, "LINE")
        bc = counter(root, "BRANCH")
        files = []
        for pkg in root.iter("package"):
            for sf in pkg.findall("sourcefile"):
                c = counter(sf, "LINE")
                if c:
                    files.append({"file": f"{pkg.get('name', '')}/{sf.get('name', '')}",
                                  "pct": pct(c[1], c[0] + c[1]), "lines": c[0] + c[1]})
        return {"tool": "jacoco", "line_pct": pct(lc[1], lc[0] + lc[1]) if lc else 0.0,
                "branch_pct": pct(bc[1], bc[0] + bc[1]) if bc and (bc[0] + bc[1]) else None, "files": files}
    print(f"warning: unrecognised coverage format: {path}", file=sys.stderr)
    return None


def git_info(repo):
    def run(*a):
        try:
            return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            return ""
    return {"commit": run("rev-parse", "--short", "HEAD"), "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
            "message": run("log", "-1", "--pretty=%s")}


def summarize(cases):
    s = {"total": len(cases), "passed": 0, "failed": 0, "error": 0, "skipped": 0, "flaky": 0, "duration": 0.0}
    for c in cases:
        s[c["status"]] += 1
        s["flaky"] += 1 if c["flaky"] else 0
        s["duration"] += c["time"]
    ran = s["total"] - s["skipped"]
    s["pass_rate"] = pct(s["passed"], ran)
    s["duration"] = round(s["duration"], 2)
    return s


def group(cases, key):
    out = {}
    for c in cases:
        out.setdefault(c[key] or "(unknown)", []).append(c)
    return {k: summarize(v) for k, v in sorted(out.items())}


def fmt_dur(sec):
    if sec < 1:
        return f"{sec * 1000:.0f} ms"
    if sec < 90:
        return f"{sec:.1f} s"
    return f"{int(sec // 60)}m {int(sec % 60)}s"


def verdict(s, cov, min_cov):
    if s["total"] == 0:
        return "NO RESULTS", "No test results were found — the run may have crashed before producing XML."
    if s["failed"] or s["error"]:
        return "FAILED", f"{s['failed'] + s['error']} of {s['total']} tests failed."
    notes = []
    if s["flaky"]:
        notes.append(f"{s['flaky']} flaky")
    if cov and min_cov is not None and cov["line_pct"] < min_cov:
        return "BELOW COVERAGE GATE", f"All tests passed but line coverage {cov['line_pct']}% < {min_cov}% gate."
    return ("PASSED WITH WARNINGS", "All tests passed; " + ", ".join(notes) + ".") if notes else \
        ("PASSED", "All executed tests passed.")


def delta(cur, prev, higher_better=True, unit=""):
    if prev is None:
        return ""
    d = round(cur - prev, 2)
    if d == 0:
        return " (no change)"
    sign = "+" if d > 0 else ""
    return f" ({sign}{d}{unit} vs previous)"


def build(args):
    files = []
    for pat in args.junit:
        files.extend(sorted(glob.glob(pat, recursive=True)))
    files = sorted(set(files))
    cases = []
    for f in files:
        cases.extend(parse_junit(f))
    cov = parse_coverage(args.coverage) if args.coverage else None
    prev = None
    if args.previous and os.path.exists(args.previous):
        try:
            prev = json.load(open(args.previous))
        except ValueError:
            print("warning: could not read --previous", file=sys.stderr)

    summ = summarize(cases)
    by_type = group(cases, "type")
    by_suite = group(cases, "suite")
    failures = [c for c in cases if c["status"] in ("failed", "error")]
    skipped = [c for c in cases if c["status"] == "skipped"]
    flaky = [c for c in cases if c["flaky"]]
    slowest = sorted(cases, key=lambda c: -c["time"])[:args.top]
    low_cov = []
    if cov:
        low_cov = sorted([f for f in cov["files"] if f["lines"] > 0], key=lambda f: f["pct"])[:args.top]

    prev_ids = {}
    new_failures, fixed = [], []
    if prev:
        prev_ids = {c["id"]: c["status"] for c in prev.get("cases", [])}
        new_failures = [c for c in failures if prev_ids.get(c["id"]) == "passed"]
        cur_ids = {c["id"]: c["status"] for c in cases}
        fixed = [i for i, st in prev_ids.items() if st in ("failed", "error") and cur_ids.get(i) == "passed"]

    v, vtext = verdict(summ, cov, args.min_coverage)
    data = {
        "title": args.title,
        "generated": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "verdict": v, "verdict_text": vtext,
        "environment": {"os": platform.platform(), "python": platform.python_version(),
                        **({"git": git_info(args.repo)} if args.repo else {})},
        "inputs": {"junit_files": files, "coverage": args.coverage},
        "summary": summ, "by_type": by_type, "by_suite": by_suite,
        "coverage": ({"tool": cov["tool"], "line_pct": cov["line_pct"], "branch_pct": cov["branch_pct"],
                      "lowest": low_cov} if cov else None),
        "previous": ({"pass_rate": prev["summary"]["pass_rate"], "total": prev["summary"]["total"],
                      "duration": prev["summary"]["duration"], "failed": prev["summary"]["failed"] + prev["summary"]["error"],
                      "flaky": prev["summary"].get("flaky", 0),
                      "coverage": (prev.get("coverage") or {}).get("line_pct")} if prev else None),
        "new_failures": [c["id"] for c in new_failures], "fixed": fixed,
        "failures": failures, "skipped": skipped, "flaky": flaky, "slowest": slowest,
        # compact case list for next run's comparison
        "cases": [{"id": c["id"], "status": c["status"], "time": c["time"]} for c in cases],
        "insights": open(args.insights, encoding="utf-8").read() if args.insights and os.path.exists(args.insights) else "",
        "min_coverage": args.min_coverage,
    }
    return data


# ---------------------------------------------------------------- Markdown
def to_markdown(d):
    s, p = d["summary"], d["previous"]
    L = [f"# {d['title']}", "", f"_Generated {d['generated']}_", "",
         f"## Verdict: {d['verdict']}", "", d["verdict_text"], ""]
    if d["insights"]:
        L += ["## Analysis & recommendations", "", d["insights"].strip(), ""]
    L += ["## Summary", "", "| Metric | Value |", "|---|---|",
          f"| Total tests | {s['total']}{delta(s['total'], p and p['total'])} |",
          f"| Passed | {s['passed']} |", f"| Failed | {s['failed']} |", f"| Errors | {s['error']} |",
          f"| Skipped | {s['skipped']} |", f"| Flaky (passed on retry) | {s['flaky']}{delta(s['flaky'], p and p['flaky'])} |",
          f"| Pass rate | {s['pass_rate']}%{delta(s['pass_rate'], p and p['pass_rate'], unit=' pts')} |",
          f"| Total test time | {fmt_dur(s['duration'])}{delta(s['duration'], p and p['duration'], unit=' s')} |"]
    if d["coverage"]:
        c = d["coverage"]
        L.append(f"| Line coverage ({c['tool']}) | {c['line_pct']}%{delta(c['line_pct'], p and p['coverage'], unit=' pts')} |")
        if c["branch_pct"] is not None:
            L.append(f"| Branch coverage | {c['branch_pct']}% |")
    L.append("")
    if d["new_failures"] or d["fixed"]:
        L += ["## Changes since previous run", ""]
        if d["new_failures"]:
            L.append(f"- **Newly failing ({len(d['new_failures'])}):** " + ", ".join(f"`{i}`" for i in d["new_failures"][:20]))
        if d["fixed"]:
            L.append(f"- **Fixed ({len(d['fixed'])}):** " + ", ".join(f"`{i}`" for i in d["fixed"][:20]))
        L.append("")

    def table(title, grp):
        out = [f"## {title}", "", "| Name | Total | Passed | Failed | Skipped | Pass rate | Time |", "|---|---|---|---|---|---|---|"]
        for k, v in grp.items():
            out.append(f"| {k} | {v['total']} | {v['passed']} | {v['failed'] + v['error']} | {v['skipped']} | {v['pass_rate']}% | {fmt_dur(v['duration'])} |")
        return out + [""]
    L += table("Results by test type", d["by_type"])
    if len(d["by_suite"]) > 1:
        L += table("Results by suite", d["by_suite"])
    L += ["## Failures", ""]
    if not d["failures"]:
        L += ["None. ✅", ""]
    for c in d["failures"]:
        L += [f"### ❌ `{c['id']}`", f"- Type: {c['type']} · Suite: {c['suite']} · Time: {fmt_dur(c['time'])}"]
        if c["message"]:
            L.append(f"- Message: {c['message'][:500]}")
        if c["detail"]:
            L += ["", "```", c["detail"][:2500], "```"]
        L.append("")
    if d["flaky"]:
        L += ["## Flaky tests (failed then passed on retry)", ""] + [f"- `{c['id']}`" for c in d["flaky"]] + [""]
    if d["skipped"]:
        L += [f"## Skipped tests ({len(d['skipped'])})", ""]
        for c in d["skipped"][:50]:
            L.append(f"- `{c['id']}`" + (f" — {c['message']}" if c["message"] else ""))
        L.append("")
    L += ["## Slowest tests", "", "| Test | Time |", "|---|---|"] + [f"| `{c['id']}` | {fmt_dur(c['time'])} |" for c in d["slowest"]] + [""]
    if d["coverage"]:
        L += ["## Least-covered files", "", "| File | Line coverage | Lines |", "|---|---|---|"]
        L += [f"| `{f['file']}` | {f['pct']}% | {f['lines']} |" for f in d["coverage"]["lowest"]] + [""]
    L += ["## Environment & inputs", "", f"- OS: {d['environment']['os']}"]
    g = d["environment"].get("git")
    if g:
        L.append(f"- Git: {g['branch']} @ {g['commit']} — {g['message']}")
    L.append(f"- JUnit files: {len(d['inputs']['junit_files'])}" + (f"; coverage: {d['inputs']['coverage']}" if d["inputs"]["coverage"] else "; no coverage file supplied"))
    return "\n".join(L) + "\n"


# -------------------------------------------------------------------- HTML
CSS = """
:root{--bg:#fff;--fg:#1d2330;--mut:#667085;--card:#f6f7f9;--bd:#e2e5ea;--ok:#1a7f4b;--bad:#c62828;--warn:#b26a00;--info:#2457c5}
@media (prefers-color-scheme:dark){:root{--bg:#14171c;--fg:#e8eaee;--mut:#9aa3b2;--card:#1d2128;--bd:#2d333d;--ok:#4cc38a;--bad:#ff6b6b;--warn:#f0b04a;--info:#7da6ff}}
*{box-sizing:border-box}body{font:15px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg);margin:0;padding:2rem 1rem}
main{max-width:1000px;margin:auto}h1{margin:.2rem 0}h2{margin-top:2.2rem;border-bottom:1px solid var(--bd);padding-bottom:.3rem}
.mut{color:var(--mut)}.banner{padding:1rem 1.2rem;border-radius:10px;margin:1rem 0;border:1px solid var(--bd);background:var(--card)}
.banner b{font-size:1.2rem}.ok{color:var(--ok)}.bad{color:var(--bad)}.warn{color:var(--warn)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.8rem;margin:1rem 0}
.tile{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:.8rem 1rem}.tile .v{font-size:1.6rem;font-weight:650}.tile .l{color:var(--mut);font-size:.8rem}
.tile .d{font-size:.78rem;color:var(--mut)}
table{border-collapse:collapse;width:100%;margin:.6rem 0;font-size:.9rem}th,td{text-align:left;padding:.45rem .6rem;border-bottom:1px solid var(--bd);vertical-align:top}th{color:var(--mut);font-weight:600}
.scroll{overflow-x:auto}code,pre{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.82rem}
pre{background:var(--card);border:1px solid var(--bd);padding:.8rem;border-radius:8px;overflow-x:auto;max-height:340px}
details{border:1px solid var(--bd);border-radius:8px;margin:.5rem 0;padding:.4rem .8rem;background:var(--card)}summary{cursor:pointer;font-weight:600}
.bar{height:8px;border-radius:4px;background:var(--bd);overflow:hidden;min-width:80px}.bar i{display:block;height:100%;background:var(--ok)}
.insights{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:.2rem 1.2rem}
"""


def esc(x):
    return html.escape(str(x))


def md_to_html(md):
    """Tiny Markdown subset: headings, bullets, numbered lists, bold, code, paragraphs."""
    out, in_ul, in_ol = [], False, False

    def inline(t):
        t = esc(t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
        return t

    def close():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
        if in_ol:
            out.append("</ol>")
        in_ul = in_ol = False

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            close()
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            close()
            lvl = min(len(m.group(1)) + 2, 5)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
        elif re.match(r"^\s*[-*]\s+", line):
            if not in_ul:
                close()
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(re.sub(r'^\s*[-*]\s+', '', line))}</li>")
        elif re.match(r"^\s*\d+[.)]\s+", line):
            if not in_ol:
                close()
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline(re.sub(r'^\s*\d+[.)]\s+', '', line))}</li>")
        else:
            close()
            out.append(f"<p>{inline(line)}</p>")
    close()
    return "\n".join(out)


def to_html(d):
    s, p = d["summary"], d["previous"]
    vcls = {"PASSED": "ok", "PASSED WITH WARNINGS": "warn", "FAILED": "bad",
            "BELOW COVERAGE GATE": "warn", "NO RESULTS": "bad"}.get(d["verdict"], "warn")

    def tile(label, value, sub="", cls=""):
        return f'<div class="tile"><div class="v {cls}">{esc(value)}</div><div class="l">{esc(label)}</div><div class="d">{esc(sub)}</div></div>'

    tiles = [
        tile("Total tests", s["total"], delta(s["total"], p and p["total"]).strip(" ()")),
        tile("Passed", s["passed"], "", "ok"),
        tile("Failed / errors", s["failed"] + s["error"], "", "bad" if s["failed"] + s["error"] else ""),
        tile("Skipped", s["skipped"]),
        tile("Flaky", s["flaky"], "", "warn" if s["flaky"] else ""),
        tile("Pass rate", f"{s['pass_rate']}%", delta(s["pass_rate"], p and p["pass_rate"], unit=" pts").strip(" ()")),
        tile("Test time", fmt_dur(s["duration"]), delta(s["duration"], p and p["duration"], unit=" s").strip(" ()")),
    ]
    if d["coverage"]:
        c = d["coverage"]
        tiles.append(tile("Line coverage", f"{c['line_pct']}%", delta(c["line_pct"], p and p["coverage"], unit=" pts").strip(" ()")))
        if c["branch_pct"] is not None:
            tiles.append(tile("Branch coverage", f"{c['branch_pct']}%"))

    def grp_table(grp):
        rows = ""
        for k, v in grp.items():
            rows += (f"<tr><td>{esc(k)}</td><td>{v['total']}</td><td>{v['passed']}</td><td>{v['failed'] + v['error']}</td>"
                     f"<td>{v['skipped']}</td><td><div class='bar'><i style='width:{v['pass_rate']}%'></i></div>{v['pass_rate']}%</td>"
                     f"<td>{fmt_dur(v['duration'])}</td></tr>")
        return ("<div class='scroll'><table><tr><th>Name</th><th>Total</th><th>Passed</th><th>Failed</th><th>Skipped</th>"
                f"<th>Pass rate</th><th>Time</th></tr>{rows}</table></div>")

    h = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
         f"<title>{esc(d['title'])}</title><style>{CSS}</style></head><body><main>",
         f"<h1>{esc(d['title'])}</h1><div class='mut'>Generated {esc(d['generated'])}</div>",
         f"<div class='banner'><b class='{vcls}'>{esc(d['verdict'])}</b> — {esc(d['verdict_text'])}</div>"]
    if d["insights"]:
        h.append(f"<h2>Analysis &amp; recommendations</h2><div class='insights'>{md_to_html(d['insights'])}</div>")
    h.append("<h2>Summary</h2><div class='grid'>" + "".join(tiles) + "</div>")
    if d["new_failures"] or d["fixed"]:
        h.append("<h2>Changes since previous run</h2><ul>")
        if d["new_failures"]:
            h.append(f"<li><b class='bad'>Newly failing ({len(d['new_failures'])}):</b> " + ", ".join(f"<code>{esc(i)}</code>" for i in d["new_failures"][:20]) + "</li>")
        if d["fixed"]:
            h.append(f"<li><b class='ok'>Fixed ({len(d['fixed'])}):</b> " + ", ".join(f"<code>{esc(i)}</code>" for i in d["fixed"][:20]) + "</li>")
        h.append("</ul>")
    h.append("<h2>Results by test type</h2>" + grp_table(d["by_type"]))
    if len(d["by_suite"]) > 1:
        h.append("<h2>Results by suite</h2>" + grp_table(d["by_suite"]))
    h.append(f"<h2>Failures ({len(d['failures'])})</h2>")
    if not d["failures"]:
        h.append("<p class='ok'>No failures.</p>")
    for c in d["failures"]:
        h.append(f"<details><summary><span class='bad'>✖</span> {esc(c['id'])}</summary>"
                 f"<p class='mut'>Type: {esc(c['type'])} · Suite: {esc(c['suite'])} · {fmt_dur(c['time'])}</p>"
                 + (f"<p>{esc(c['message'][:600])}</p>" if c["message"] else "")
                 + (f"<pre>{esc(c['detail'][:3000])}</pre>" if c["detail"] else "") + "</details>")
    if d["flaky"]:
        h.append("<h2>Flaky tests</h2><p class='mut'>Failed at least once, then passed on retry.</p><ul>"
                 + "".join(f"<li><code>{esc(c['id'])}</code></li>" for c in d["flaky"]) + "</ul>")
    if d["skipped"]:
        h.append(f"<h2>Skipped tests ({len(d['skipped'])})</h2><ul>" + "".join(
            f"<li><code>{esc(c['id'])}</code>" + (f" — {esc(c['message'])}" if c["message"] else "") + "</li>" for c in d["skipped"][:50]) + "</ul>")
    h.append("<h2>Slowest tests</h2><div class='scroll'><table><tr><th>Test</th><th>Time</th></tr>"
             + "".join(f"<tr><td><code>{esc(c['id'])}</code></td><td>{fmt_dur(c['time'])}</td></tr>" for c in d["slowest"]) + "</table></div>")
    if d["coverage"]:
        h.append("<h2>Least-covered files</h2><div class='scroll'><table><tr><th>File</th><th>Line coverage</th><th>Lines</th></tr>"
                 + "".join(f"<tr><td><code>{esc(f['file'])}</code></td><td>{f['pct']}%</td><td>{f['lines']}</td></tr>" for f in d["coverage"]["lowest"])
                 + "</table></div>")
    g = d["environment"].get("git")
    h.append("<h2>Environment &amp; inputs</h2><ul>"
             f"<li>OS: {esc(d['environment']['os'])}</li>"
             + (f"<li>Git: {esc(g['branch'])} @ {esc(g['commit'])} — {esc(g['message'])}</li>" if g else "")
             + f"<li>JUnit files: {len(d['inputs']['junit_files'])}"
             + (f"; coverage: {esc(d['inputs']['coverage'])}" if d["inputs"]["coverage"] else "; no coverage file supplied") + "</li></ul>")
    h.append("</main></body></html>")
    return "".join(h)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--junit", nargs="+", required=True, help="JUnit XML path(s) or glob(s)")
    ap.add_argument("--coverage")
    ap.add_argument("--previous")
    ap.add_argument("--insights")
    ap.add_argument("--repo")
    ap.add_argument("--title", default="Test Report")
    ap.add_argument("--out", default="test-report", help="output path prefix (no extension)")
    ap.add_argument("--top", type=int, default=10, help="rows in slowest / least-covered tables")
    ap.add_argument("--min-coverage", type=float, default=None, help="optional line-coverage gate (percent)")
    args = ap.parse_args()

    data = build(args)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out + ".md", "w", encoding="utf-8") as fh:
        fh.write(to_markdown(data))
    with open(args.out + ".html", "w", encoding="utf-8") as fh:
        fh.write(to_html(data))
    with open(args.out + ".json", "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    s = data["summary"]
    print(f"{data['verdict']}: {s['passed']}/{s['total']} passed, {s['failed'] + s['error']} failed, "
          f"{s['skipped']} skipped, {s['flaky']} flaky")
    print(f"Wrote {args.out}.html, {args.out}.md, {args.out}.json  (use the .json as --previous next run)")
    sys.exit(0)


if __name__ == "__main__":
    main()
