#!/usr/bin/env python3
"""Static, offline, read-only audit of a skill folder.

Never executes anything from the skill. Standard library only. Makes no network calls.

Usage:
  audit_skill.py <skill-dir> [--format json|markdown]
  audit_skill.py --compare <old-dir> <new-dir> [--format json|markdown]

Findings are heuristics: absence of findings is NOT proof of safety.
"""
import argparse, hashlib, json, re, sys, unicodedata
from pathlib import Path

SEV = ["info", "low", "medium", "high", "critical"]
TEXT_EXT = {".md", ".txt", ".py", ".sh", ".js", ".ts", ".json", ".yaml", ".yml", ".toml",
            ".html", ".css", ".cfg", ".ini", ".rules", ""}
MAX_BYTES = 2_000_000

# (id, severity, regex, message) applied to every text file
PATTERNS = [
    ("inject-override", "high", r"ignore (all |any )?(previous|prior|above) (instructions|rules)|disregard (the )?(system|previous)", "Instruction-override phrasing"),
    ("conceal", "high", r"(do not|don't|never) (tell|inform|show|reveal to) the user|without (telling|informing|notifying) the user|hide (this|these) (action|step)s?", "Instructs concealment from user"),
    ("skip-consent", "medium", r"without (asking|confirmation|approval|permission)|skip (the )?(confirmation|approval|review)", "Bypasses confirmation"),
    ("secret-aws", "critical", r"AKIA[0-9A-Z]{16}", "AWS access key ID"),
    ("secret-private-key", "critical", r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "Private key material"),
    ("secret-token", "critical", r"(?i)\b(gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,})", "API token pattern"),
    ("secret-assign", "high", r"(?i)\b(api[_-]?key|secret|passw(or)?d|token)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]", "Hard-coded credential-like value"),
    ("pii-email", "low", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "Email address (check if real/personal)"),
    ("pipe-to-shell", "high", r"(curl|wget)[^\n|]*\|\s*(sudo\s+)?(ba|z)?sh", "Remote script piped to shell"),
    ("destructive", "high", r"\brm\s+-rf?\s+(/|~|\$HOME|\*)|mkfs\.|dd\s+if=.*of=/dev/|:\(\)\s*\{", "Destructive command"),
    ("cred-paths", "high", r"~/\.ssh|~/\.aws|\.netrc|\.git-credentials|Login Data|keychain|/etc/shadow", "References credential locations"),
    ("exec-dynamic", "high", r"\b(eval|exec)\s*\(|os\.system\(|subprocess\.[a-z_]+\([^)]*shell\s*=\s*True|child_process", "Dynamic/shell execution"),
    ("subprocess", "medium", r"\bsubprocess\.|\bPopen\(|os\.popen\(", "Subprocess use"),
    ("network-code", "medium", r"\b(requests|httpx|aiohttp|urllib\.request|http\.client)\.\w+\(|socket\.socket\(|\bfetch\(|\b(curl|wget|ncat?)\s+(-\S+\s+)*\S*(https?://|\$)", "Network-capable code or command"),
    ("obfuscation", "high", r"base64\.b64decode|atob\(|fromCharCode|\\x[0-9a-fA-F]{2}(\\x[0-9a-fA-F]{2}){8,}|codecs\.decode\([^)]*rot", "Possible obfuscation/decoding"),
    ("unpinned-install", "medium", r"pip3?\s+install(?!.*==)|npm\s+(i|install)(?!.*@\d)|npx\s+(?!.*@\d)", "Unpinned package install"),
    ("html-comment", "medium", r"<!--.{20,}?-->", "Long HTML comment (possible hidden text)"),
    ("telemetry", "medium", r"(?i)telemetry|analytics|beacon|report (back|to) (the )?(server|author|developer)", "Possible telemetry"),
    ("wildcard-perm", "medium", r"(?i)allowed[-_]tools\s*:\s*.*(\*|bash\(\*\))|permissions?\s*:\s*\[?\s*['\"]?\*", "Wildcard permission"),
]
URL_RE = re.compile(r"https?://[^\s<>\)\]\"'`]+")
HIDDEN_CHARS = {"\u200b", "\u200c", "\u200d", "\u2060", "\ufeff", "\u202a", "\u202b", "\u202c",
                "\u202d", "\u202e", "\u2066", "\u2067", "\u2068", "\u2069"}


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[m.end():]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def audit(root: Path):
    findings, files, urls, caps = [], [], set(), set()

    def add(sev, fid, msg, f="", line=0, ev=""):
        findings.append({"severity": sev, "id": fid, "message": msg, "file": f, "line": line, "evidence": ev[:160]})

    if not root.is_dir():
        add("critical", "not-a-dir", f"{root} is not a directory")
        return {"root": str(root), "findings": findings, "files": [], "urls": [], "capabilities": []}

    skill_md = None
    for name in ("SKILL.md", "skill.md", "AGENTS.md"):
        if (root / name).exists():
            skill_md = root / name
            break
    if skill_md is None:
        add("high", "no-instruction-file", "No SKILL.md/AGENTS.md found")

    for p in sorted(root.rglob("*")):
        rel = str(p.relative_to(root))
        if p.is_symlink():
            add("high", "symlink", "Symlink present (could point outside skill)", rel)
            continue
        if not p.is_file():
            continue
        size = p.stat().st_size
        files.append({"path": rel, "bytes": size, "sha256": sha(p)})
        if p.suffix == ".py" or p.suffix in {".sh", ".js", ".ts"}:
            caps.add("scripts")
        if size > MAX_BYTES:
            add("low", "large-file", f"File larger than {MAX_BYTES} bytes, skipped content scan", rel)
            continue
        if p.suffix.lower() not in TEXT_EXT:
            add("info", "binary-asset", "Non-text file, content not scanned", rel)
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            add("medium", "non-utf8", "File not valid UTF-8; could hide content", rel)
            continue
        if p.suffix in {".sh"} or text.startswith("#!"):
            caps.add("executable-script")
        for ln, line in enumerate(text.splitlines(), 1):
            if any(c in HIDDEN_CHARS for c in line):
                add("high", "hidden-unicode", "Zero-width/bidi control character", rel, ln)
            if len(line) > 1000:
                add("medium", "long-line", "Very long line (possible hidden payload)", rel, ln)
            for fid, sev, rx, msg in PATTERNS:
                if re.search(rx, line, re.I if fid.startswith("inject") or fid in ("conceal", "skip-consent") else 0):
                    # don't flag detection rules inside this audit tool's own docs/examples at info level only
                    add(sev, fid, msg, rel, ln, line.strip())
                    if fid in ("network-code", "pipe-to-shell"):
                        caps.add("network")
                    if fid in ("subprocess", "exec-dynamic"):
                        caps.add("process-exec")
                    if fid == "cred-paths":
                        caps.add("credential-access")
            for u in URL_RE.findall(line):
                urls.add(u.rstrip(".,;"))
        for m in re.finditer(r"<!--.*?-->", text, re.S):
            if len(m.group(0)) > 40 and "html-comment" not in {f["id"] for f in findings if f["file"] == rel}:
                add("medium", "html-comment", "Long HTML comment (possible hidden text)", rel,
                    text[:m.start()].count("\n") + 1, m.group(0))

    if skill_md:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        fm, body = parse_frontmatter(text)
        n = len(text.splitlines())
        if fm is None:
            add("medium", "no-frontmatter", "Missing YAML frontmatter", skill_md.name)
        else:
            if not fm.get("name"):
                add("medium", "no-name", "Frontmatter lacks name", skill_md.name)
            elif fm["name"] != root.resolve().name and not root.resolve().name.endswith(".skill"):
                add("low", "name-mismatch", f"name '{fm['name']}' != folder '{root.resolve().name}'", skill_md.name)
            d = fm.get("description", "")
            if not d:
                add("high", "no-description", "Frontmatter lacks description (skill cannot trigger)", skill_md.name)
            elif len(d) < 60:
                add("low", "short-description", "Description very short; may under-trigger", skill_md.name)
            elif len(d) > 1024:
                add("low", "long-description", "Description over 1024 chars", skill_md.name)
            for k in fm:
                if k.lower() in ("allowed-tools", "allowed_tools", "tools", "permissions"):
                    caps.add(f"declares:{k}")
        if n > 500:
            add("low", "long-skill", f"Instruction file is {n} lines; consider progressive disclosure", skill_md.name)
        # referenced files that don't exist
        for ref in set(re.findall(r"`((?:references|scripts|assets)/[^`\s]+)`", text)):
            if not (root / ref.rstrip("/")).exists():
                add("low", "missing-ref", f"Referenced path not found: {ref}", skill_md.name)

    findings.sort(key=lambda f: (-SEV.index(f["severity"]), f["file"], f["line"]))
    if urls:
        caps.add("external-urls")
    return {"root": str(root), "findings": findings, "files": files,
            "urls": sorted(urls), "capabilities": sorted(caps)}


def counts(res):
    c = {s: 0 for s in SEV}
    for f in res["findings"]:
        c[f["severity"]] += 1
    return c


def verdict(res):
    c = counts(res)
    if c["critical"]:
        return "DO NOT USE until critical findings are resolved"
    if c["high"]:
        return "HIGH-RISK findings need human review before use"
    if c["medium"]:
        return "Review medium findings; no blockers found by static checks"
    return "No blocking findings from static checks (not proof of safety)"


def compare(old, new):
    of = {f["path"]: f["sha256"] for f in old["files"]}
    nf = {f["path"]: f["sha256"] for f in new["files"]}
    ofind = {(f["id"], f["file"], f["evidence"]) for f in old["findings"]}
    nfind = [f for f in new["findings"] if (f["id"], f["file"], f["evidence"]) not in ofind]
    return {
        "files_added": sorted(set(nf) - set(of)),
        "files_removed": sorted(set(of) - set(nf)),
        "files_modified": sorted(p for p in nf if p in of and nf[p] != of[p]),
        "capabilities_added": sorted(set(new["capabilities"]) - set(old["capabilities"])),
        "capabilities_removed": sorted(set(old["capabilities"]) - set(new["capabilities"])),
        "urls_added": sorted(set(new["urls"]) - set(old["urls"])),
        "urls_removed": sorted(set(old["urls"]) - set(new["urls"])),
        "new_findings": nfind,
        "requires_approval": bool(set(new["capabilities"]) - set(old["capabilities"])
                                  or set(new["urls"]) - set(old["urls"])
                                  or any(f["severity"] in ("high", "critical") for f in nfind)),
    }


def md_audit(res):
    c = counts(res)
    out = [f"# Audit: {res['root']}", "", f"**Verdict:** {verdict(res)}", "",
           "Counts: " + ", ".join(f"{k}={v}" for k, v in c.items()), "",
           f"Capabilities detected: {', '.join(res['capabilities']) or 'none'}", ""]
    if res["urls"]:
        out += ["## External URLs", *[f"- {u}" for u in res["urls"]], ""]
    out += ["## Findings"]
    if not res["findings"]:
        out.append("None from static checks.")
    for f in res["findings"]:
        loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
        ev = f" — `{f['evidence']}`" if f["evidence"] else ""
        out.append(f"- **{f['severity'].upper()}** [{f['id']}] {f['message']} ({loc}){ev}")
    out += ["", "## Not checked", "- Semantic intent, runtime behavior, dependency contents, "
            "binary assets, obfuscation beyond simple patterns. Heuristics can miss things and over-report."]
    return "\n".join(out)


def md_compare(d):
    out = ["# Capability / change diff", "", f"**Requires explicit approval:** {'YES' if d['requires_approval'] else 'no'}", ""]
    for k in ("files_added", "files_removed", "files_modified", "capabilities_added",
              "capabilities_removed", "urls_added", "urls_removed"):
        out.append(f"- {k}: {', '.join(d[k]) or 'none'}")
    out.append("")
    out.append("## New findings")
    if not d["new_findings"]:
        out.append("None.")
    for f in d["new_findings"]:
        out.append(f"- **{f['severity'].upper()}** [{f['id']}] {f['message']} ({f['file']}:{f['line']})")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?")
    ap.add_argument("--compare", nargs=2, metavar=("OLD", "NEW"))
    ap.add_argument("--format", choices=["json", "markdown"], default="markdown")
    a = ap.parse_args()
    if a.compare:
        d = compare(audit(Path(a.compare[0])), audit(Path(a.compare[1])))
        print(json.dumps(d, indent=2) if a.format == "json" else md_compare(d))
        return 1 if d["requires_approval"] else 0
    if not a.path:
        ap.error("provide a skill directory or --compare OLD NEW")
    res = audit(Path(a.path))
    res["verdict"] = verdict(res)
    res["counts"] = counts(res)
    print(json.dumps(res, indent=2) if a.format == "json" else md_audit(res))
    return 2 if res["counts"]["critical"] else (1 if res["counts"]["high"] else 0)


if __name__ == "__main__":
    sys.exit(main())
