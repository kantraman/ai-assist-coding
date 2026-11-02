---
name: secure-code-forge
description: Write production-grade code that is secure, maintainable and performant by construction, then automatically review it against those same criteria and against the user's intended behavior before delivering it. Use this skill whenever the user asks Claude to write, implement, build, scaffold, refactor or fix code (APIs, services, scripts, CLIs, libraries, web apps, database access, auth, file handling, infrastructure code), whether or not they mention security or quality, and for anything beyond a trivial one-liner. Also use it when the user asks to review, audit, harden or sanity-check existing code for security holes, performance problems, maintainability, or whether it actually does what was intended. Make sure to use it when the user mentions "production", "best practices", "secure", "code review", "vulnerabilities", "clean code" or "optimize".
---

# Secure Code Forge

Code that merely works is the easy part. The failures that hurt later are the quiet ones: an unvalidated input, an N+1 query, a function nobody can change safely, or a feature that drifted from what was asked. This skill builds the quality in while writing, then makes Claude review its own output as a skeptical outsider and fix what it finds, so what reaches the user has already been through a review.

The loop: **Intent → Design → Generate → Review → Fix → Deliver.**

## Step 0: Pick the depth

Scale effort to risk so small tasks stay fast and risky ones get scrutiny.

| Tier | When | What changes |
|---|---|---|
| Light | Pure functions, local scripts, no untrusted input | Brief intent, quick review pass, 1 fix round |
| Standard | Typical app/service code | Full workflow below |
| Deep | Handles untrusted input, authn/authz, secrets, money, PII, file/network/process access, deserialization, crypto, multi-tenant data | Full workflow plus explicit threat sketch, security-negative tests, up to 3 fix rounds |

When in doubt, go one tier up. State the tier in one line.

## Step 1: Intent contract

Before writing code, pin down what "correct" means, because the later conformance check needs something to check against. Use `assets/intent-contract.md` as the shape. For Light tasks, a few lines inline is enough.

Capture:
- **Goal** in one or two sentences.
- **Numbered requirements** (R1, R2, ...) that are individually testable.
- **Non-goals**, so scope creep is detectable.
- **Trust boundaries**: where data enters from users, files, networks, other services.
- **Security requirements**: authn/authz model, sensitive data, compliance constraints.
- **Performance expectations**: realistic scale (rows, requests/sec, payload size) and latency budget. If unknown, state an assumed scale.
- **Constraints**: language, framework, dependencies, style, test framework.

Ask the user only when a wrong guess would be costly or irreversible (e.g. the auth model, the data store, the target runtime). Otherwise state assumptions explicitly in the contract and move on. Show the contract to the user briefly; they can correct it cheaply now rather than expensively later.

## Step 2: Design sketch (Standard and Deep)

- List assets worth protecting, entry points, and trust boundaries. For Deep, run a quick STRIDE pass (spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege) and note which requirement or control answers each credible threat.
- Choose data structures and algorithms with the expected scale in mind; note the complexity of hot paths.
- Prefer the standard library and well-maintained, widely used dependencies. Every added dependency is attack surface and maintenance cost, so justify each one.

## Step 3: Generate

Write the code to disk (a file in `/mnt/user-data/outputs/`), not just in chat, so the review step reads the real artifact.

Apply these defaults while writing. The reasons matter: they let you handle cases not listed here.

**Secure by construction**
- Treat all external input as hostile; validate at the boundary with allowlists (type, length, range, format) and reject, don't "clean".
- Separate code from data: parameterized queries, argument arrays instead of shell strings, templating with auto-escaping, safe parsers. Injection is always a failure to keep these apart.
- Enforce authorization server-side on every object access, not just at login. Fail closed.
- Secrets come from the environment or a secret manager, never source, logs or error messages.
- Use vetted crypto libraries and current algorithms; never invent schemes. Compare secrets in constant time; generate tokens with a CSPRNG.
- Bound everything an attacker can inflate: request size, recursion depth, timeouts, pagination, retries, concurrency.
- Secure defaults: TLS verification on, least privilege, restrictive file permissions, CORS/CSP tight, debug off.
- Errors tell the user what to do, tell the logs what happened, and never leak internals.

**Performant by design**
- Right algorithm and data structure first; micro-optimizations only where measurement or clear reasoning says they matter.
- No queries or I/O inside loops (N+1); batch, stream or paginate. Bound concurrency; avoid unbounded memory growth.
- Reuse connections and expensive objects; cache only with a clear invalidation story.
- Comment non-obvious complexity assumptions ("O(n log n), n ≤ 1e6 expected").

**Maintainable**
- Small single-purpose functions, clear names, explicit types or type hints, shallow nesting.
- Configuration separated from logic; side effects at the edges, pure logic in the middle.
- Comments explain *why*, not *what*. No dead code, no unrequested features.
- Tests alongside the code: requirement-driven tests, edge cases, and for Standard/Deep **security-negative tests** (malicious input is rejected, unauthorized access is denied).

Detailed checklists: `references/security-checklist.md`, `references/performance-checklist.md`, `references/maintainability-checklist.md`. Read the one(s) relevant to the code's domain before generating when the task is Standard or Deep.

## Step 4: Automated review (never skip)

Review the files as they exist on disk. Re-read them with `view` rather than relying on memory of what you meant to write; the gap between intention and artifact is exactly where bugs hide.

**4a. Tool pass.** Run `bash scripts/static_checks.sh <path-to-code>`. It runs a built-in offline pattern scan (`scripts/pattern_scan.py`), a Python complexity check (`scripts/complexity_check.py`), and any installed linters/scanners (bandit, ruff, semgrep, eslint, gosec, shellcheck, gitleaks, etc.), noting clearly which were unavailable. Triage every finding: real, false positive (say why), or accepted risk. The built-in scan is line-based, so it misses multi-line patterns (e.g. an `except:` followed by `pass` on the next line) and anything data-flow related; that is what 4b is for. A clean tool run is never a clean bill of health.

**4b. Adversarial read.** You wrote this, so you are biased toward thinking it is fine. Counter that: switch to a reviewer's stance, assume at least one real defect exists, and go lens by lens:
1. **Security lens**: walk each trust boundary from `references/security-checklist.md`. Trace tainted data from source to sink. Ask "what if this input is huge, empty, malformed, hostile, or concurrent?"
2. **Performance lens**: find the hot path, state its complexity, look for N+1, unbounded growth, blocking calls, repeated work.
3. **Maintainability lens**: long functions, deep nesting, duplication, hidden coupling, missing tests, unclear names, swallowed errors.
4. **Conformance lens** (cross-check with intent): build a traceability table: each requirement R# → where implemented → which test covers it → status (met / partial / missing). Then list **unrequested behavior** in the code (scope creep, extra endpoints, extra data collected). Both gaps and extras are findings.

If the environment supports subagents (Claude Code, Cowork), delegate 4b to a separate reviewer given only the intent contract and the code, not your generation reasoning. A fresh context catches what the author's context rationalizes away. In plain chat, do the lenses as separate sequential passes.

**4c. Execute.** Run the tests and, where safe, the code itself. A review that never executes anything misses the basics.

Record each finding as: `[severity] location - what's wrong - why it matters - fix`. Severity rubric:
- **Critical**: exploitable now or data loss (injection, auth bypass, exposed secret, RCE).
- **High**: serious weakness or a requirement not met.
- **Medium**: robustness, performance cliff at expected scale, significant maintainability debt.
- **Low**: style, minor clarity, nice-to-have.

## Step 5: Fix loop

Fix all Critical and High findings and any Medium that is cheap, edit the files, then rerun Step 4 on the changed code. Fixes can introduce new bugs, so the re-review is part of the fix. Stop when no Critical/High remains and every requirement is met, or after 3 rounds (then report what remains rather than looping forever). Anything knowingly left is listed as an accepted risk with reasoning.

## Step 6: Deliver

Present the code files, followed by a short review summary in the format of `assets/review-report-template.md`: tier, what was checked, tools run (and tools unavailable), findings fixed, remaining accepted risks, the requirements traceability table, and how to run the tests.

Be honest about limits. Never say the code "is secure"; say what was checked and what was not (e.g. "no dependency audit: network unavailable", "not penetration tested"). Overclaiming is itself a security risk because it discourages the human review that should still happen for Deep-tier code.

## Combining with other skills

- Formal review report as a file: use the `docx` or `pdf` skill. Findings tracker: `xlsx`.
- UI code: use `frontend-design` for look and feel, but still apply the XSS/CSP/session items in the security checklist.
- Uploaded code to review: use `file-reading` to load it, then start at Step 4.
- Code that calls Anthropic APIs: consult `product-self-knowledge` so model names, limits and SDK usage are current.

## Review-only requests

If the user supplies existing code and wants an audit, skip Steps 2-3. Infer or ask for the intent (what the code should do), then run Step 4 and deliver findings with proposed fixes; apply fixes only if asked.
