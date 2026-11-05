# Output templates

## Trade-off matrix
Weights sum to 100. Scores 1 to 5 (5 = best for the user's constraints). Always add a justification line.

| Axis (weight) | Option A | Option B | Option C |
|---|---|---|---|
| Axis 1 (30) | 4: why | 2: why | 5: why |
| Axis 2 (25) | ... | ... | ... |
| Weighted total | | | |

**Choice:** ... **Flips if:** (e.g., "if write volume exceeds X/s, prefer B")

## Pruned options
- Option D: dropped because (one line)

## Premortem table
| # | Failure mode | Likelihood | Impact | Detection | Mitigation (design/test/monitor) |
|---|---|---|---|---|---|

## Second-order notes
- 1 week: ...
- 6 months: ...
- 2 years: ...
- One-way doors: ...

## Test plan
- Happy path: ...
- Boundaries: ...
- Invalid/hostile input: ...
- Failure/timeout/partial: ...
- Concurrency/idempotency: ...
- Mitigation tests: ...
- Regression: ...

## Red-team checklist (apply what is relevant)
**Input and injection:** SQL/NoSQL/command/template injection; XSS; path traversal; SSRF; XXE; unsafe deserialization; regex DoS; unbounded size/depth/count.
**Authn/authz:** missing or client-side-only checks; IDOR/BOLA; privilege escalation; weak session/token handling; confused deputy.
**Secrets and data:** hardcoded credentials; secrets in logs/errors/URLs; PII exposure; weak crypto or homegrown crypto; missing encryption in transit/at rest.
**Concurrency and state:** race conditions, TOCTOU, double-spend/double-submit, non-idempotent retries, lost updates, deadlocks, shared mutable state.
**Resources:** leaks (memory, file handles, connections), missing timeouts, unbounded queues/caches, amplification loops.
**Errors:** swallowed exceptions, stack traces leaked to users, fail-open behavior, partial writes without rollback.
**Supply chain:** unnecessary or unpinned dependencies, untrusted install scripts.
**LLM/agent features:** prompt-injection via retrieved or user content, tool calls without allow-lists or confirmation, data exfiltration through outputs, over-broad tool permissions, untrusted output rendered or executed.
**Operability:** missing logging/metrics/alerts, no rollback path, unsafe migrations.

## Decision record (for architectural work)
- **Context:** ...
- **Decision:** ...
- **Alternatives considered:** ...
- **Consequences (positive/negative):** ...
- **Revisit when:** ...

## Review findings
| Severity | Location | Issue | Fix |
|---|---|---|---|
