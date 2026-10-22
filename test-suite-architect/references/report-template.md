# Test report: required contents and insight writing

`scripts/generate_report.py` produces the factual sections automatically. This file defines what a *complete* report contains, so you can fill the gaps (insights, scope, risks) and adapt the format when asked.

## Required sections (in order)
1. **Title, date, scope** — project, commit/branch, environment, which test types were run **and which were not** (and why).
2. **Verdict** — one line: PASSED / PASSED WITH WARNINGS / FAILED / BLOCKED (couldn't run), plus what it means for release.
3. **Executive summary (insights)** — 3–6 sentences or bullets: overall health, top risks, what needs a decision.
4. **Summary metrics** — total, passed, failed, errors, skipped, flaky, pass rate, duration, coverage; deltas vs. previous run if available.
5. **Results by test type and by suite.**
6. **Failures** — each with test id, message, trace, type; grouped by probable root cause in the insights.
7. **Flaky and skipped tests** — with reasons and owners if known.
8. **Performance of the suite** — slowest tests, total duration vs. budget.
9. **Coverage** — totals, branch if available, least-covered files, mapped to risk (are the uncovered files important?).
10. **Trends** — newly failing, fixed, metric changes.
11. **Gaps and risks** — untested areas, missing test types, environment limitations, assumptions.
12. **Recommendations** — ordered, specific, with effort/impact (e.g. "Add refund-rounding regression test — S effort, closes the failure in `OrderTotalTest`").
13. **Appendix** — environment details, commands used, raw result file locations.

## Writing `insights.md` (embedded via `--insights`)
Keep it to roughly one screen. Template:

```markdown
## Executive summary
- **Verdict:** FAILED — 3 failures in checkout; do not release until fixed.
- 412 tests, 97.1% pass; unit and API layers healthy; E2E not run (no staging URL available).
- Coverage 78% (+2 pts); payment module remains at 41%.

## Failures by probable cause
1. **Real defect (2 tests):** refunds round half-down instead of half-up — `test_refund_rounding[...]`. Evidence: expected 10.05, got 10.04; logic in `billing/refund.py:88`.
2. **Test defect (1 test):** `test_dashboard_loads` depends on wall-clock time; passes locally, fails after midnight UTC.

## Risks and gaps
- No integration tests for the payment webhook handler.
- 14 tests skipped without reason in `legacy/`.

## Recommendations
1. Fix refund rounding and keep the new regression test (S).
2. Inject a clock into the dashboard test (S).
3. Add webhook integration tests using Testcontainers/Postgres (M).
4. Introduce a coverage ratchet at 78% in CI (S).
```

Guidelines:
- Facts must trace to the data; label hypotheses as such ("likely", "suspected") and say how to confirm.
- Distinguish **product defects**, **test defects**, **environment/infrastructure issues**.
- Don't pad: if everything passed, say so briefly and focus on gaps and trends.
- Never hide a failed or unrun suite behind an aggregate pass rate.

## Alternate formats
- **Word / PDF for stakeholders:** generate the `.md`/`.html` first, then use the docx or pdf skill with the same sections; keep the verdict and summary on page 1.
- **Slide/one-pager:** verdict, 4 headline metrics, top 3 risks, top 3 actions.
- **Bug list for a tracker:** one entry per root cause: title, severity, steps/test id, expected vs. actual, suspected location, linked failing tests.
- **CI summary (GitHub step summary):** append the `.md` to `$GITHUB_STEP_SUMMARY`.
- **Other result formats** (TAP, Go JSON, NUnit XML, Allure): convert to JUnit XML first (`go-junit-report`, `tap-junit`, `trx2junit`, etc.) so the generator can read them; or extend `parse_junit()` in the script.
