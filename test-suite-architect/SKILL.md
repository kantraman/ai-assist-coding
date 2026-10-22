---
name: test-suite-architect
description: Analyze a code repository and design, implement, improve, and report on its automated testing — unit, integration, regression, end-to-end (E2E), API/contract, smoke, performance, and security tests. Use this skill whenever the user wants to add tests or a testing framework to a project, audit or fix an existing test suite (flaky tests, low coverage, slow tests, weak assertions, redundant tests), set up test tooling or CI test stages, build a regression suite, measure test effectiveness (coverage, mutation testing), or produce a test report/summary after a test run. Trigger even if the user only says things like "this repo has no tests", "our tests are a mess", "how well tested is this code?", "set up Jest/pytest/Playwright/JUnit", "write a test plan", or "give me a test report" — they don't need to say "testing framework".
---

# Test Suite Architect

Turn a repository into one with a test suite that is *appropriate, runnable, trustworthy, and measurable* — then report on it honestly.

A test suite is only valuable if it catches real bugs, runs reliably, and runs fast enough that people actually use it. Coverage numbers alone don't prove that. Keep that in mind at every phase: the goal is confidence in the code, not a green dashboard.

## The workflow

Work through these phases in order. Phases 1–2 are always needed; later phases depend on the request (e.g. "just give me a report" → jump to Phase 6, but still sanity-check Phase 1 context).

1. **Recon** — understand the repo
2. **Strategy** — decide what to test, with which tools, and at what level
3. **Implement** — set up frameworks and write the tests
4. **Improve** — audit and strengthen existing tests
5. **Run** — execute with machine-readable output
6. **Report** — generate the test report
7. **Feed back** — use results to make the suite more effective

Tell the user which phase you're in as you go, and confirm the strategy (Phase 2) before writing large amounts of test code, since it's the cheapest point to correct course.

---

## Phase 1 — Recon

Run the analyzer first; it does the deterministic part (detecting languages, manifests, existing tests, CI, and untested modules) so you can spend your effort on judgment:

```bash
python /path/to/test-suite-architect/scripts/analyze_repo.py <repo-root> --format markdown
# or --format json to process programmatically
```

Then read the code that matters, because the script is heuristic. Specifically look at:

- **Entry points and architecture**: Is it a library, CLI, web service, SPA, mobile app, data pipeline, monorepo? This determines which test types make sense.
- **Where the risk lives**: business logic, money/auth/permissions, parsing, concurrency, external integrations, data migrations. Risk — not file count — should drive test priority.
- **Seams for testing**: dependency injection, interfaces, config for external URLs/DBs. Hard-to-test code is a finding worth reporting; suggest the smallest refactor that makes it testable rather than mocking around it.
- **Existing test conventions**: naming, directory layout, fixtures, mocking style. Match them unless they're clearly harmful — consistency beats personal preference.
- **How the project is built and run**: Can you actually install dependencies and run the app/tests here? Try the existing test command before assuming anything. If it can't run (no network, missing services), say so and adapt: write tests carefully, state they're unexecuted, and still provide the exact commands for the user.

Summarize recon in a short brief: stack, current test state (what exists, does it pass, rough coverage if obtainable), top risks, and obvious gaps.

## Phase 2 — Strategy

Produce a concise **test strategy** (a table or short list, not an essay):

| Test type | Worth doing here? | Tool | Scope / first targets |
|---|---|---|---|

Guidance for choosing:

- **Follow the test pyramid, bent to the project.** Many fast unit tests, fewer integration tests, a *small* number of E2E tests covering critical user journeys. Inverting this (mostly E2E) makes suites slow and flaky. Libraries and pure-logic code lean on unit tests; CRUD-heavy services lean on integration/API tests; UIs need component tests plus a thin E2E layer.
- **Prefer the framework already in use.** Only introduce a new one when nothing exists or the current one is blocking (unmaintained, can't do what's needed). Justify any switch.
- **Pick the mainstream tool for the ecosystem** when starting fresh — see `references/frameworks.md` for a selection table by language and test type.
- **Don't add test types for their own sake.** A CLI tool doesn't need browser E2E; a static site may need only a smoke test and link check. Say "not applicable" where true.
- **Regression tests** are bug-driven: each fixed bug gets a test that fails before the fix and passes after. When setting up a regression suite from scratch, build it from (a) the project's bug history/issues/changelog if available, (b) golden/snapshot tests of stable public behavior, and (c) a tagged "critical path" smoke subset that runs on every commit. See `references/test-types.md`.
- **Define the quality gates up front**: what must pass in CI, coverage floor (a ratchet — "never decrease" — beats an arbitrary 80%), max runtime for the PR-gating subset.

Ask the user only about things you can't infer and that materially change the plan (e.g. "Is there a staging environment E2E can target?", "Are tests allowed to hit a real database via Docker?"). Offer a sensible default alongside each question.

## Phase 3 — Implement

Read `references/test-types.md` for the detailed how-to per test type, and `references/frameworks.md` for setup snippets. The principles:

**Set up infrastructure before writing many tests.**
- Install/configure the runner, assertion lib, and mocking tools; add scripts (`npm test`, `pytest`, `mvn test`, `make test`) so one command runs everything and others run subsets (`test:unit`, `test:integration`, `test:e2e`).
- Configure **machine-readable output from day one** — JUnit XML plus a coverage XML/lcov file — because Phase 6 consumes them. See the framework table for the flags.
- Separate test types by directory or markers/tags so they can run independently in CI.
- Add test data management: factories/builders over giant static fixtures; deterministic seeds; ephemeral resources (containers, temp dirs, in-memory DBs) that tests create and tear down themselves.
- Add or extend CI config (GitHub Actions, GitLab CI, etc.) so fast tests gate PRs and slow ones run on merge/nightly. Keep it to what the user's platform already uses.

**Write tests that are worth keeping.**
- Test *behavior through the public interface*, not implementation details; tests coupled to internals break on every refactor and teach nothing.
- One behavior per test, descriptive names (`rejects_expired_token`, not `test1`), Arrange–Act–Assert layout.
- Cover the happy path, boundaries, error paths, and the odd inputs (empty, null, huge, unicode, concurrent). Examine the code for branches and invariants rather than echoing the happy-path example.
- Assertions must be able to fail. An assertion-free test, or `assert result is not None` on something that's never None, is noise.
- Mock only at the boundary you don't own (network, clock, filesystem, third-party APIs). Over-mocking produces tests that pass while production breaks. For internal collaborators, prefer real objects or lightweight fakes.
- Make tests independent and order-agnostic; never depend on another test's side effects or wall-clock time/sleeps (use explicit waits/conditions and injected clocks).
- E2E: use stable selectors (`data-testid`/roles), page objects or helper layers, auto-waiting, and test only critical journeys.

**Verify what you write.** Run the tests. Make sure new tests actually pass, and for a sample of important ones, confirm they can fail (temporarily break the code or invert an assertion). If you can't execute them, say so plainly in your summary.

**Never "fix" a failing test by weakening it.** If a new test fails, decide whether it exposed a real bug (report it — that's the point), a wrong assumption, or an environment issue. Don't silently modify production code unless the user asked; surface suspected bugs with evidence.

## Phase 4 — Improve an existing suite

When a suite exists, audit before adding more. Read `references/improving-existing.md` for the full checklist. In brief, assess:

- **Reliability**: flaky tests (rerun the suite several times or use `--reruns`/retry reports), order dependence, timing/sleep usage, shared state.
- **Speed**: slowest tests, missing parallelism, expensive setup that could be shared, E2E tests that should be integration tests.
- **Effectiveness**: weak/missing assertions, over-mocking, tests of trivial getters, duplicated tests, coverage of *risky* code vs. total coverage, mutation score where tooling permits.
- **Maintainability**: duplicated setup (extract fixtures/builders), unclear names, giant tests, dead/skipped tests that have rotted.
- **Structure**: missing test types, mixed unit/integration in one folder, no CI gate, no machine-readable output.

Deliver the audit as a prioritized list (impact vs. effort), then implement the top items. Make changes incrementally and re-run after each so regressions are attributable. Don't mass-rewrite a working suite to match your taste.

## Phase 5 — Run

Run the suites with JUnit XML (and coverage) output to a known folder, e.g. `test-results/`:

```bash
# examples — adapt to the project; more in references/frameworks.md
pytest --junitxml=test-results/unit.xml --cov --cov-report=xml:test-results/coverage.xml
npx jest --ci --reporters=default --reporters=jest-junit --coverage --coverageReporters=lcov
mvn test            # surefire XML lands in target/surefire-reports/
go test ./... -json | go-junit-report > test-results/unit.xml
```

Run each test type separately when possible so the report can break results down by type. Record wall-clock time and the environment (OS, runtime versions, commit SHA). If a run crashes before producing XML (compile error, missing dependency), that is itself a result — report it, don't hide it.

## Phase 6 — Report

Generate the report from the raw results:

```bash
python /path/to/test-suite-architect/scripts/generate_report.py \
  --junit "test-results/*.xml" \
  --coverage test-results/coverage.xml \
  --title "Acme API — Test Report" \
  --repo . \
  --out test-report \
  [--previous test-report-prev.json] \
  [--insights insights.md]
```

It writes `test-report.html` (shareable), `test-report.md`, and `test-report.json` (keep it; pass it as `--previous` on the next run for trend comparison). It covers: overall verdict and pass rate, results by test type and suite, every failure with message and trace, skipped tests, flaky tests, slowest tests, coverage totals plus least-covered files, and deltas against a previous run.

The script reports facts. **You add the judgment**: write an `insights.md` (executive summary, what the failures mean, probable root causes, risk assessment, prioritized recommendations) and pass it with `--insights` so it's embedded at the top. Good insights:

- Lead with the verdict and what it means for shipping ("3 failures, all in payment refunds — block release").
- Group failures by likely root cause instead of listing 40 symptoms.
- Separate *real defects*, *test defects* (bad test/flaky), and *environment problems*.
- Say what was **not** tested or not run. An honest "E2E didn't run: no staging URL" matters more than a pretty pass rate.
- End with a short, ordered action list.

Required report contents are listed in `references/report-template.md` — read it if the user wants a custom format (PDF, Word, a slide, Jira-ready bug list). For a Word/PDF deliverable, generate the HTML/MD first and then use the docx or pdf skill.

Present the final report file(s) to the user and summarize the headline in a few sentences in chat; don't paste the whole report.

## Phase 7 — Feed results back (effectiveness loop)

After a report, close the loop so the suite improves over time:

1. Turn each real failure into a ticket/note with a minimal reproduction; turn each fixed bug into a permanent regression test.
2. Quarantine flaky tests (tagged, tracked, non-blocking) with an owner and a deadline — never leave them silently skipped.
3. Target the lowest-covered *high-risk* files first for new tests; use mutation testing (`references/improving-existing.md`) on critical modules to check that the tests actually detect changes.
4. Set or tighten the coverage ratchet and the CI time budget.
5. Re-run and generate a new report with `--previous` so trends (pass rate, coverage, duration, flaky count) are visible.

Offer these as next steps; do the ones the user agrees to.

---

## Principles to keep in mind

- **Evidence over assertion.** Don't claim tests pass, coverage is X%, or a bug exists without a run or a reading of the code to back it.
- **Be candid about limits.** Coverage ≠ quality; a green suite ≠ correct software. Say what the suite does and doesn't protect.
- **Respect the repo.** Match the stack, style, and tooling; keep diffs reviewable; don't add heavy dependencies for marginal value; don't touch production code without saying so.
- **Safety.** Never commit secrets into test config; use env vars and fake credentials. E2E and performance tests must not target production systems unless the user explicitly says so. Don't run destructive tests against shared data.
- **Scale to the repo.** For a huge monorepo, analyze and strategize per package, start with the highest-risk package, and avoid trying to do everything in one pass.

## Bundled files

- `scripts/analyze_repo.py` — repo reconnaissance (languages, manifests, test frameworks, CI, untested modules). Stdlib only.
- `scripts/generate_report.py` — builds HTML/Markdown/JSON test reports from JUnit XML + coverage (Cobertura, JaCoCo, lcov). Stdlib only.
- `references/frameworks.md` — tool selection and setup/output flags by language and test type.
- `references/test-types.md` — what each test type is for, how to build it, anti-patterns.
- `references/improving-existing.md` — audit checklist, flakiness, mutation testing, effectiveness metrics.
- `references/report-template.md` — required report sections and insight-writing guidance.
