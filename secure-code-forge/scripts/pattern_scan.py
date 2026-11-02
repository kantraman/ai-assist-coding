#!/usr/bin/env python3
"""Offline, dependency-free scan for risky code patterns across common languages.

Usage: pattern_scan.py <path> [--json]
Exit code: 2 if any HIGH/CRITICAL finding, else 0.
Heuristic: expect false positives; triage each finding.
"""
import json, os, re, sys

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", "target", ".mypy_cache"}
EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go", ".rb", ".php", ".rs", ".c", ".h",
        ".cpp", ".cs", ".sh", ".bash", ".yml", ".yaml", ".json", ".env", ".tf", ".sql", ".html", ".dockerfile"}

# (id, severity, cwe, description, regex)
RULES = [
    ("hardcoded-secret", "CRITICAL", "CWE-798", "Possible hardcoded credential",
     r"""(?i)\b(password|passwd|secret|api[_-]?key|token|private[_-]?key)\b\s*[:=]\s*['"][^'"\s]{8,}['"]"""),
    ("aws-key", "CRITICAL", "CWE-798", "AWS access key id", r"\bAKIA[0-9A-Z]{16}\b"),
    ("private-key", "CRITICAL", "CWE-798", "Private key material", r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    ("eval-exec", "HIGH", "CWE-95", "Dynamic code execution (eval/exec/new Function)",
     r"(?<![\w.])(eval|exec)\s*\(|new\s+Function\s*\("),
    ("shell-true", "HIGH", "CWE-78", "Shell invocation with possible injection", r"shell\s*=\s*True|os\.system\s*\(|child_process\.exec\s*\(|Runtime\.getRuntime\(\)\.exec"),
    ("sql-concat", "HIGH", "CWE-89", "SQL built via string formatting/concatenation",
     r"""(?i)(execute|query|raw)\s*\(\s*(f['"]|['"].*(select|insert|update|delete)\b.*['"]\s*(\+|%|\.format))|(select|insert|update|delete)\b[^\n]*(\+\s*\w+|\{\w+\}|%s['"]?\s*%)"""),
    ("unsafe-deserialize", "HIGH", "CWE-502", "Unsafe deserialization", r"pickle\.loads?\(|marshal\.loads?\(|yaml\.load\((?!.*SafeLoader)|ObjectInputStream|unserialize\("),
    ("tls-verify-off", "HIGH", "CWE-295", "TLS verification disabled", r"verify\s*=\s*False|rejectUnauthorized\s*:\s*false|InsecureSkipVerify\s*:\s*true|CURLOPT_SSL_VERIFYPEER\s*,\s*(false|0)"),
    ("xss-sink", "HIGH", "CWE-79", "Raw HTML sink with possibly untrusted data", r"\.innerHTML\s*=|dangerouslySetInnerHTML|document\.write\(|v-html"),
    ("weak-hash", "MEDIUM", "CWE-327", "Weak hash/cipher for security use", r"(?i)\b(md5|sha1)\b\s*[\(\.]|hashlib\.(md5|sha1)|MessageDigest\.getInstance\(\s*['\"](MD5|SHA-1)|DES|ECB"),
    ("insecure-random", "MEDIUM", "CWE-338", "Non-cryptographic RNG (check if used for tokens/secrets)", r"Math\.random\(|\brandom\.(random|randint|choice)\(|\brand\(\)"),
    ("debug-on", "MEDIUM", "CWE-489", "Debug mode enabled", r"(?i)\bdebug\s*=\s*True|app\.run\([^)]*debug\s*=\s*True|NODE_ENV\s*=\s*['\"]?development"),
    ("cors-wildcard", "MEDIUM", "CWE-942", "Wildcard CORS", r"""(?i)Access-Control-Allow-Origin['"]?\s*[:,]\s*['"]\*|origin\s*:\s*['"]\*['"]|allow_origins\s*=\s*\[\s*['"]\*"""),
    ("bind-all", "LOW", "CWE-668", "Binds to all interfaces", r"0\.0\.0\.0"),
    ("tmp-predictable", "MEDIUM", "CWE-377", "Predictable temp file", r"mktemp\(|['\"]/tmp/[\w.-]+['\"]"),
    ("perm-777", "MEDIUM", "CWE-732", "World-writable permissions", r"chmod\s+(-R\s+)?0?777|0o?777"),
    ("swallowed-error", "MEDIUM", "CWE-390", "Swallowed exception", r"except\s*(Exception)?\s*:\s*(pass|\.\.\.)\s*$|catch\s*\([^)]*\)\s*\{\s*\}"),
    ("jwt-none", "HIGH", "CWE-347", "JWT verification disabled or alg none", r"(?i)verify_signature['\"]?\s*:\s*False|algorithms\s*=\s*\[\s*['\"]none|alg['\"]?\s*:\s*['\"]none"),
    ("http-url", "LOW", "CWE-319", "Cleartext http:// URL (non-local)", r"http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])[\w.-]+"),
    ("todo-security", "LOW", "-", "Unresolved security TODO", r"(?i)(TODO|FIXME|HACK).{0,40}(secur|auth|valid|sanitiz|escape|encrypt)"),
]
COMPILED = [(i, s, c, d, re.compile(r)) for i, s, c, d, r in RULES]
ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def iter_files(root):
    if os.path.isfile(root):
        yield root
        return
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if os.path.splitext(f)[1].lower() in EXTS or f in {"Dockerfile", ".env"}:
                yield os.path.join(d, f)


def scan(root):
    out = []
    for path in iter_files(root):
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                for n, line in enumerate(fh, 1):
                    if len(line) > 2000:
                        continue
                    for rid, sev, cwe, desc, rx in COMPILED:
                        if rx.search(line):
                            out.append({"file": path, "line": n, "rule": rid, "severity": sev,
                                        "cwe": cwe, "desc": desc, "code": line.strip()[:140]})
        except OSError:
            pass
    out.sort(key=lambda f: (ORDER[f["severity"]], f["file"], f["line"]))
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    findings = scan(args[0])
    if "--json" in sys.argv:
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            print(f"[{f['severity']}] {f['file']}:{f['line']} {f['rule']} ({f['cwe']}) {f['desc']}\n    {f['code']}")
        print(f"\n{len(findings)} pattern finding(s). Heuristic scan: triage each as real / false positive / accepted risk.")
    sys.exit(2 if any(f["severity"] in ("CRITICAL", "HIGH") for f in findings) else 0)
