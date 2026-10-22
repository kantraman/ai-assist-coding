# Improving an existing test suite and measuring its effectiveness

Contents: audit procedure · flaky tests · slow tests · weak tests · mutation testing · coverage done right · metrics to track · prioritizing

## Audit procedure
1. **Run it.** Does it run with one command? How long? Does it pass on a clean checkout? Run 3× to expose flakiness (`pytest --count=3` via pytest-repeat, `--repeat-each=3` in Playwright, or a shell loop).
2. **Get machine-readable output** (JUnit XML + coverage) — add if missing — then run `scripts/generate_report.py` to get the baseline report.
3. **Run `scripts/analyze_repo.py`** for structure, skipped markers, assertion-free files, and unmatched sources.
4. **Sample-read** 10–15 tests from different areas, favoring the largest and the most-recently-failing. Judge them against the quality bar in `test-types.md`.
5. **Write findings as a prioritized list** (impact × effort), each with evidence (file, test name, number).

## Flaky tests
Symptoms: pass/fail changes without code change; fail only in CI, only in parallel, only at certain times.
Common causes and fixes:
| Cause | Fix |
|---|---|
| Fixed `sleep`/timeouts | Wait on a condition (auto-wait, polling helper, event) |
| Shared state / order dependence | Isolate data per test; reset in setup/teardown; randomize order (`pytest-randomly`) to expose |
| Real time / randomness | Inject clock and seed RNG (`freezegun`, fake timers, fixed seed) |
| Async races | Await the actual completion signal; avoid asserting before promises settle |
| External network | Stub third-party calls; pin versions of containers |
| Resource limits in CI | Reduce parallelism; give services health checks before tests start |
| Non-deterministic ordering (maps, DB without ORDER BY) | Sort before asserting |
Process: reproduce (loop it), identify the cause, fix; if not fixable now, **quarantine** (tag, move to a non-blocking job, create a tracked issue with owner + date). Do not leave it silently skipped or retried forever — retries hide problems; use them to *detect* flakiness, and report it.

## Slow tests
- Use the report's "slowest tests" table; profile with `pytest --durations=20`, `jest --verbose`, Gradle/Maven reports.
- Parallelize (`pytest-xdist -n auto`, Jest workers, Playwright `workers`, Maven `-T`), sharding in CI.
- Share expensive setup (session/class-scoped fixtures, one container per suite) while keeping data isolated.
- Push logic down the pyramid: an E2E test checking a validation rule should be a unit test.
- Split into tiers: fast PR gate (<10 min target, ideally <5) vs. slower nightly.
- Cache dependencies and browser binaries in CI.

## Weak or low-value tests
Look for and fix:
- No assertions / assertions that can't fail (`assert True`, `expect(x).toBeDefined()` on a literal).
- Only checking "no exception thrown" for functions with meaningful outputs.
- Over-mocked: every collaborator mocked, test asserts mock calls → passes while real behavior is broken.
- Tests that copy the implementation (recomputing the expected value with the same formula).
- Giant tests that check 20 behaviors, so one failure hides the others.
- Duplicated tests; tests for trivial code; commented-out or `skip`ped tests that are never revisited (delete or fix).
- Snapshot tests updated blindly.
- Hard-coded environment assumptions (absolute paths, local ports, timezone).
Improve by: strengthening assertions to check outcomes, replacing mock-heavy tests with fakes/real objects, splitting large tests, parametrizing duplicates, extracting builders/fixtures.

## Mutation testing (checks that tests actually detect bugs)
Mutation tools make small code changes ("mutants": flip `>` to `>=`, remove a call, change a constant) and see if any test fails. Surviving mutants = behavior your tests don't pin down.
- Python: `mutmut run --paths-to-mutate src/pkg/critical.py` → `mutmut results`
- JS/TS: `npx stryker run` (configure `mutate` globs)
- Java: PIT (`mvn org.pitest:pitest-maven:mutationCoverage`)
- Others: Go `go-mutesting`, Rust `cargo-mutants`, .NET Stryker.NET
Apply to **critical modules only** (it's slow). Report mutation score (killed / total) and the top surviving mutants; add tests that kill them. A module with 95% line coverage but 40% mutation score has weak assertions.
Manual alternative when tooling can't run: pick important functions, deliberately break them (off-by-one, wrong operator, delete a branch), and confirm a test fails; revert after.

## Coverage — use it correctly
- Coverage finds *untested code*; it does not prove tested behavior. Treat high coverage with weak assertions as a red flag.
- Prefer **branch coverage** where supported; line coverage hides untested conditions.
- Look at coverage **by risk**: 60% overall with 95% in payment/auth is better than 85% overall with 20% in payment.
- Gate with a **ratchet** (fail if coverage drops vs. main; or require coverage on changed lines via `diff-cover`/Codecov patch coverage) instead of a flat 80% that encourages junk tests.
- Exclude generated code, vendored code, and trivial boilerplate explicitly in config — and document why.

## Effectiveness metrics to track across reports
| Metric | Healthy direction | Notes |
|---|---|---|
| Pass rate on main | ~100% | Persistent red teaches people to ignore tests |
| Flaky test count | → 0 | Track quarantined tests |
| PR-gate duration | stable/falling | Budget it (e.g. ≤10 min) |
| Line / branch coverage (and on changed code) | non-decreasing | Ratchet |
| Mutation score (critical modules) | rising | Strongest quality signal available |
| Defect escape rate | falling | Bugs found in prod that no test caught; each becomes a regression test |
| Time to diagnose failure | falling | Good names/messages, traces, screenshots |
| Skipped/disabled count | falling | Each needs an owner |
`generate_report.py --previous <old>.json` shows deltas for pass rate, duration, coverage, flaky and newly failing/fixed tests.

## Prioritizing improvements
1. Make the suite runnable and reliable (one command, green on clean checkout, flaky fixed/quarantined).
2. Wire into CI with machine-readable output and a ratchet.
3. Add tests for the highest-risk, least-covered code (use the report's least-covered table + the analyzer's untested list + your read of the domain).
4. Strengthen weak tests in critical areas (mutation testing).
5. Speed up.
6. Refactor for maintainability.
Do 1–2 before 3: new tests on an unreliable base add noise.
