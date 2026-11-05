# Quality Gates

Each priority gets an operational definition and a check. A task is done only when the gates relevant to its size pass. Report what was run and what was not.

## Contents
1. Per-priority gates
2. Security checklist
3. Testing strategy
4. Definition of done
5. Threat model (lightweight)

## 1. Per-priority gates

| Priority | Operational meaning | Check |
|---|---|---|
| **Accuracy** | Behavior matches requirements; edge cases handled | every requirement traces to a test (graph validator); boundary, empty, null, large, concurrent cases; property tests for pure logic; money/time handled with correct types |
| **Security** | Abuse resistant, data protected | checklist in section 2; dependency audit; secrets scan; authz tests with deny cases |
| **Testability** | Cheap, fast, deterministic tests | pure Core; ports for I/O; injectable clock/random/ids; unit suite under a minute; no test depends on order or network |
| **Maintainability** | Easy for a stranger to change safely | layer rules pass; low coupling and cycle-free graph; small functions; names from the domain; lint/format/type-check clean; no dead code |
| **Scalability** | Grows by adding resources, not rewriting | stateless app tier; shared state in DB/cache/queue; idempotent jobs; pagination everywhere; load test at 2 to 3x expected peak |
| **Performance** | Meets latency/throughput/size budgets | budgets measured, not assumed; query plans reviewed; bundle and web-vitals budgets in CI; GA tuning only after profiling |
| **Flexibility** | Swap parts without surgery | adapters behind ports; config and feature flags; no vendor types in Core |
| **Evolution** | Safe to change for years | expand/contract migrations; additive API changes; ADRs; fitness functions in CI; ontology/manifests current; deprecation policy |

## 2. Security checklist

**Input and output**: parameterized queries or ORM binding only (no string-built SQL); schema validation at every boundary; context-aware output encoding; no `eval`/dynamic code from input; safe file upload (type sniffing, size caps, random names, outside web root, scan if needed); safe deserialization.

**AuthN/AuthZ**: vetted auth library; password hashing with Argon2id/bcrypt; MFA option; session rotation and expiry; object-level authorization on every access; deny by default; admin functions separately protected.

**Web**: CSRF protection for cookie auth; `HttpOnly`/`Secure`/`SameSite` cookies; CSP, `X-Content-Type-Options`, frame protections, HSTS; CORS with exact origins; no secrets or tokens in URLs or `localStorage`; subresource integrity for third-party scripts.

**Server and data**: SSRF-safe outbound requests (allow-lists, block internal ranges); TLS everywhere; encryption at rest for sensitive fields; PII minimized, classified, and excluded from logs; least-privilege DB user (no DDL at runtime); tenant isolation tests; rate limiting and lockout; request size and timeout limits.

**Supply chain and ops**: pinned and audited dependencies (lockfiles, `npm audit`/`pip-audit`/OWASP dependency-check), minimal base images, secrets in a manager and never committed, CI secret scanning, structured audit logging for security events, error responses that do not leak internals, backups with restore tests.

## 3. Testing strategy

- **Unit** (Core): fast, many, pure. **Contract** (module and API boundaries). **Integration** (Adapters against real DB/queue via containers, not mocks of the DB). **End-to-end** (few, critical journeys). **Non-functional**: load, security (SAST, DAST, dependency), accessibility.
- Write the failing test from the requirement first; keep tests asserting behavior, not implementation.
- Coverage is a smoke detector, not a goal: look at uncovered branches in critical logic. Mutation testing on the most critical modules if available.
- Deterministic data builders over giant fixtures; freeze time; seed randomness.

## 4. Definition of done

- Requirements implemented and traced to tests; tests pass (state which you ran).
- Lint, format, and type checks clean; graph validation passes.
- Security checklist reviewed for the touched surface; no new high-severity audit findings.
- Migration is backward compatible and reversible.
- Budgets measured where the change could affect them.
- Docs updated: contract, manifest, ADR if a non-obvious decision was made.
- Observability: logs/metrics/traces for new paths, with module ids.

## 5. Threat model (lightweight STRIDE)

For each new trust boundary (browser to API, API to DB, API to third party), ask: Spoofing (who is the caller?), Tampering (can input or data be altered?), Repudiation (is there an audit trail?), Information disclosure (what leaks?), Denial of service (what is unbounded?), Elevation of privilege (can a user act as another or as admin?). Record the top risks as `Risk` nodes with `mitigates` edges.
