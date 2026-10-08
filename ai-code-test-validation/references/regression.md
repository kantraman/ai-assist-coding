# Regression Testing Strategies

## Contents
- Choosing the type
- Bug-repro workflow
- Characterization workflow
- Contract and schema tests
- Snapshot/golden tests: rules
- Organizing and running in CI
- Regression after AI changes code

## Choosing the type
| Situation | Use |
|---|---|
| A bug was found/fixed | Bug-repro test named after the issue |
| Legacy code without tests is about to be changed/rewritten | Characterization tests first |
| Other systems/clients depend on outputs | Contract/schema tests |
| Large deterministic output (reports, rendered HTML, generated SQL) | Golden/snapshot tests with reviewed diffs |
| Critical business flow (checkout, login, payout) | Few end-to-end/integration smoke tests |
| Refactor or AI rewrite claimed to be "behavior-preserving" | Differential test: run old and new implementation on the same inputs (including generated/random ones) and compare |

## Bug-repro workflow
1. Write the test reproducing the reported behavior at the highest stable level (public function/endpoint).
2. Run it on the buggy code: it **must fail for the right reason** (read the failure message).
3. Apply the fix. Run: it passes.
4. Name/tag it with the issue id. Add neighboring cases (same root cause elsewhere, boundaries near the bug).

## Characterization workflow
1. Identify the public entry points that will be affected.
2. Feed representative and edge inputs, record actual outputs (this is the only place where "run it and capture" is acceptable).
3. Review each recorded output with the user or against known business behavior; label suspected bugs as `KNOWN_QUIRK` with a comment instead of silently blessing them.
4. Commit the tests **before** modifying code. After the change, differences must be explained as intended or fixed.

## Contract and schema tests
Validate against the machine-readable contract (OpenAPI, JSON Schema, protobuf, GraphQL schema) when one exists; otherwise pin field names, types, nullability, enum values, status codes, error format, and ordering guarantees. Include "unknown field ignored" and "missing optional field" cases.

## Snapshot/golden rules
- Keep snapshots small and human-reviewable; normalize volatile parts (timestamps, ids, ordering).
- Never regenerate snapshots to fix a red run without reading the diff and confirming it is intended.
- Prefer explicit assertions on key fields; use snapshots as a complement, not a replacement.

## Organizing and CI
- Mark regression tests (`@pytest.mark.regression`, JUnit `@Tag("regression")`, xUnit `[Trait("Category","Regression")]`, Jest project/describe naming, Go build tags or `-run` prefixes).
- Fast unit tests on every commit; slower regression/integration on PR and nightly.
- Fail the build on flaky tests being retried silently; quarantine explicitly with an issue link.

## Regression after AI changes code
When AI edits existing code: (1) run the full existing suite before and after; (2) diff behavior with a differential test on the touched module; (3) check the diff for unrelated edits (renames, removed checks, changed defaults) and add a test for each behavior that changed unintentionally; (4) confirm removed code had no callers or tests relying on it.
