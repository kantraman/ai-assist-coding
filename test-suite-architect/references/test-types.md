# Test types: purpose, construction, pitfalls

Contents: unit · integration · API/contract · regression · end-to-end · smoke · component/UI · performance · security · property-based · snapshot/golden · choosing the mix

## Unit tests
**Purpose:** verify one unit of logic (function/class) in isolation; fast (ms), deterministic.
**Build:**
- Target pure logic, branching, validation, calculations, state machines, parsers.
- Cover: typical input, boundaries (0, 1, max, empty), invalid input/exceptions, and each branch.
- Use table-driven/parametrized tests for many input→output cases.
- Replace slow/non-deterministic collaborators (clock, random, network, FS) — not every collaborator.
**Pitfalls:** asserting on private methods or call counts of internal mocks; tests that mirror the implementation line-by-line; testing framework code or trivial getters.

## Integration tests
**Purpose:** verify that real components work together: service + DB, repository + schema, module + message queue, service + another service.
**Build:**
- Use real infrastructure where practical (Testcontainers/Docker Compose/in-memory DB with the same dialect).
- Each test creates its own data and cleans up (transaction rollback, unique IDs, truncation).
- Run migrations in test setup so schema drift is caught.
- Fake only third-party systems you can't run (payment gateway, email) using recorded fixtures or a stub server (WireMock, MSW, nock, responses).
**Pitfalls:** shared mutable test DB; order dependence; tests that need a developer's local state; hidden network calls.

## API / contract tests
**Purpose:** verify HTTP/GraphQL/gRPC behavior — status codes, schema, auth, error shapes — and consumer/provider compatibility.
**Build:** call the app in-process (supertest, TestClient, MockMvc) or against a running instance; assert status, body schema, headers, auth (no token, wrong role, expired), pagination, validation errors, idempotency. If an OpenAPI spec exists, validate responses against it (Schemathesis/Dredd). For multi-service systems add consumer-driven contracts (Pact).

## Regression tests
**Purpose:** ensure previously working behavior and previously fixed bugs stay fixed.
**Build — three complementary sources:**
1. *Bug-driven:* for every bug fix, write the test first, confirm it fails on the buggy code, then passes after the fix. Name it after the issue (`test_issue_1423_refund_rounds_half_up`) and keep it forever.
2. *Behavior-locking (characterization/golden) tests:* when code lacks tests and must be refactored, capture current outputs for representative inputs (snapshot/golden files) before changing it. Review snapshots by eye; don't blindly update them.
3. *Critical-path suite:* tag a small, fast subset (`@smoke`/`@critical`) of the most important flows to run on every commit; run the full regression nightly or pre-release.
**Mining history:** if git history/issue tracker is available, scan commits mentioning "fix", "bug", "regression", "hotfix" to find areas with churn and bugs; prioritize tests there.
**Pitfalls:** snapshot sprawl nobody reviews; regression suite that only grows and never gets pruned/deduped; skipping the "fails before the fix" check.

## End-to-end (E2E) tests
**Purpose:** verify critical user journeys through the whole stack (UI → API → DB) as a user would.
**Build:**
- Pick 5–20 journeys that make or lose money or trust: sign-up/login, checkout, core create/edit flow, permissions boundary.
- Use Playwright/Cypress; stable locators (role, label, `data-testid`); rely on auto-waiting, never fixed sleeps.
- Seed data through APIs or DB fixtures, not through the UI; log in via API/stored auth state to skip repeated UI login.
- Run against an ephemeral/staging environment, never production; isolate test accounts/data.
- Keep each test independent and under ~1–2 minutes; capture traces/screenshots/video on failure.
- Use a thin page-object/helper layer for repeated flows.
**Pitfalls:** testing edge cases through the browser (push them down to unit/integration); shared accounts; timing-based waits; too many E2E tests → slow and flaky suite.

## Smoke tests
Minimal "is it alive and are the critical paths working" checks: app boots, health endpoint OK, DB reachable, login works, one core transaction succeeds. Run after every deploy. Target < 2 minutes.

## Component / UI tests
Render a component in isolation (Testing Library, Storybook interaction tests, Vue Test Utils), interact like a user, assert on visible output and accessibility roles. Mock the network with MSW. Add axe checks for accessibility. Use visual regression (Playwright screenshots/Chromatic) sparingly for design-system components.

## Performance / load tests
Define SLOs first (p95 latency, throughput, error rate). Script realistic user flows (k6/Locust/Gatling), ramp load, assert thresholds, and run against a production-like environment, never prod. Benchmarks for hot paths (`pytest-benchmark`, JMH, `go test -bench`) with regression thresholds. Keep out of the PR gate; run nightly or pre-release.

## Security tests
SAST (Semgrep, Bandit, CodeQL), dependency scanning (npm audit, pip-audit, Trivy, Dependabot), secret scanning (gitleaks), and targeted tests for authz (can user A read user B's data?), input validation/injection, rate limiting. DAST (OWASP ZAP) against a test deployment. Report findings by severity.

## Property-based and fuzz tests
Instead of examples, state invariants ("decode(encode(x)) == x", "sorted output is a permutation of input") and let Hypothesis / fast-check / jqwik / `go test -fuzz` generate inputs. High value for parsers, serializers, encoders, calculators, and anything handling untrusted input.

## Snapshot / golden-file tests
Good for large structured outputs (rendered HTML, CLI output, generated code, API payloads). Keep snapshots small and readable, review diffs in code review, and never auto-update without looking.

## Choosing the mix (rule of thumb)
| Project type | Emphasis |
|---|---|
| Library / SDK | Heavy unit + property-based; examples as doc tests; API compatibility tests |
| Backend service | Unit for domain logic; integration with real DB; API tests; few E2E smoke flows; contract tests if microservices |
| Web app (SPA) | Unit + component tests; API mocked with MSW; ~10 Playwright journeys; a11y checks |
| CLI tool | Unit + golden-output tests; run the binary in temp dirs for integration |
| Data pipeline | Unit tests on transforms; small fixture datasets; schema/data-quality checks; idempotency tests |
| Mobile app | Unit (logic/view-models); a few UI tests per core flow on emulators |
| Legacy code without tests | Characterization/golden tests first, then refactor behind them |

## Quality bar for any test
A good test (1) fails when the behavior breaks, (2) passes reliably, (3) has a name that states the behavior, (4) is independent, (5) is fast for its level, (6) is readable without the source open.
