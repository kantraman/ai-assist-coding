# Security Checklist

Use as a walk-through at each trust boundary. Not every item applies; skip with a reason, don't skip silently. CWE ids are for traceability.

## Contents
1. Input & injection
2. AuthN / AuthZ / sessions
3. Secrets & crypto
4. Data protection & logging
5. Files, network, processes
6. Web-specific
7. Dependencies & supply chain
8. Concurrency & resource abuse
9. Language notes

## 1. Input & injection
- Validate type, length, range, format with allowlists at the boundary; reject on failure (CWE-20).
- SQL/NoSQL/LDAP: parameterized queries or ORM bindings; never string-built queries (CWE-89). Dynamic identifiers (table/column) only from a fixed allowlist.
- OS commands: no shell; pass argv arrays; never interpolate input (CWE-78).
- Templates/HTML: auto-escaping on; no raw `innerHTML`/`dangerouslySetInnerHTML` with untrusted data (CWE-79). Context-appropriate encoding (HTML, attr, JS, URL).
- Deserialization: no pickle/unsafe YAML/Java native/`eval` on untrusted data; use JSON with schema validation (CWE-502).
- XML: disable external entities and DTDs (CWE-611).
- Regex: avoid catastrophic backtracking on user input (CWE-1333); cap input length.
- Log/header injection: strip CR/LF from values placed in headers/logs (CWE-93/117).

## 2. AuthN / AuthZ / sessions
- Authorization check on every request for every object (IDOR/BOLA, CWE-639, CWE-862). Derive identity from the session/token, never from a client-supplied user id.
- Deny by default; role checks centralized, not scattered.
- Passwords: Argon2id/bcrypt/scrypt with per-user salt; never reversible or fast hashes (CWE-916).
- Sessions/JWT: random unguessable ids, rotate on login, expiry, `HttpOnly; Secure; SameSite`; verify signature, `alg`, `exp`, `aud`, `iss`; no `alg: none`.
- Rate-limit and lock out login, reset, OTP, and enumeration-prone endpoints (CWE-307). Generic error messages.
- CSRF protection for cookie-authenticated state-changing requests (CWE-352).

## 3. Secrets & crypto
- No secrets in source, config committed to VCS, images, logs, or error text (CWE-798, CWE-532).
- CSPRNG for tokens/keys/IVs (`secrets`, `crypto.randomBytes`, `SecureRandom`); never `random`/`Math.random` (CWE-338).
- AES-GCM / ChaCha20-Poly1305 for encryption; unique nonce per message; SHA-256+ for hashing; HMAC for integrity; no MD5/SHA-1/DES/ECB for security (CWE-327).
- TLS verification never disabled (`verify=False`, `rejectUnauthorized:false`, `InsecureSkipVerify`) (CWE-295).
- Constant-time comparison for secrets/MACs (CWE-208).

## 4. Data protection & logging
- Collect and keep the minimum; encrypt sensitive data at rest and in transit.
- Never log credentials, tokens, full card numbers, or PII; mask where needed.
- Errors to clients are generic; stack traces and SQL stay in server logs (CWE-209).
- Security-relevant events (login failure, authz denial, admin action) are logged with who/what/when.

## 5. Files, network, processes
- Path traversal: resolve to canonical path and check it stays under the allowed base; reject `..`, absolute paths, symlink escapes (CWE-22).
- Uploads: allowlist extension and verify content type, cap size, store outside web root with generated names, never execute (CWE-434).
- SSRF: for user-supplied URLs allowlist scheme/host, block private/link-local/metadata IPs after DNS resolution, disable redirects or re-validate (CWE-918).
- Temp files: `mkstemp`/`NamedTemporaryFile`, not predictable names (CWE-377). Restrictive permissions (0600/0700).
- Timeouts on every network call; limit response sizes.
- Run with least privilege; no root; drop capabilities.

## 6. Web-specific
- Security headers: CSP, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, HSTS, frame-ancestors.
- CORS: explicit origins, never `*` with credentials.
- Open redirects: allowlist redirect targets (CWE-601).
- Mass assignment: bind only allowlisted fields to models (CWE-915).
- Content-Type enforced; JSON parsers with size limits.

## 7. Dependencies & supply chain
- Minimal, maintained, pinned dependencies with lockfile; no abandoned packages; check for known CVEs (`pip-audit`, `npm audit`, `cargo audit`, `govulncheck`) when network allows.
- Verify package names (typosquatting); no `curl | sh` in build steps.
- Dockerfiles: pinned base images, non-root user, no secrets in layers.

## 8. Concurrency & resource abuse
- Race conditions on check-then-act (TOCTOU) over files/balances/inventory; use transactions, locks, or atomic operations (CWE-362, CWE-367).
- Bound request size, pagination, recursion, decompression ratio (zip bombs), batch size, queue depth (CWE-400, CWE-770).
- Idempotency for retried operations that move money or send messages.

## 9. Language notes
- **Python**: no `eval/exec/pickle/yaml.load`; `subprocess.run([..], shell=False)`; `secrets` not `random`; `defusedxml`; `assert` is not validation (stripped under -O).
- **JavaScript/TypeScript**: beware prototype pollution (`__proto__`, deep merge of user objects); `child_process.execFile` over `exec`; avoid `eval`/`new Function`; validate with a schema library (zod/ajv).
- **Java/Kotlin**: `PreparedStatement`; disable XXE factories; no native deserialization of untrusted data.
- **Go**: check every `err`; `exec.Command` with args; `html/template` not `text/template` for HTML; context timeouts.
- **Rust**: `unsafe` blocks justified and minimal; avoid `unwrap()` on external input; integer overflow in release builds.
- **C/C++**: bounds-checked APIs, no `gets/strcpy/sprintf`; integer overflow before allocation; prefer safer abstractions.
- **SQL/IaC**: least-privilege DB roles; no public buckets/security groups open to 0.0.0.0/0; encryption on.
