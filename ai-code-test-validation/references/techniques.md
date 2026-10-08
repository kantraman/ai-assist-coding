# Test Design Techniques

## Contents
1. Equivalence partitioning
2. Boundary value analysis
3. Decision tables
4. State transitions
5. Property-based testing
6. Error-path and negative testing
7. Test doubles: what to fake and what not to
8. Independent oracles

## 1. Equivalence partitioning
Split inputs into classes the code should treat the same; test one representative per class, plus each invalid class.
Example, discount for order total: `<0 (invalid)`, `0..99.99 (no discount)`, `>=100 (10%)`, `non-numeric (invalid)`.

## 2. Boundary value analysis
Bugs cluster at edges. For every threshold `T` test `T-1 unit`, `T`, `T+1 unit`. Also: 0, 1, -1, empty, max size, max int, first/last element, single-element collection, exactly-at-limit pagination, midnight, month/year end, leap day, DST change.
For money use the smallest currency unit around the threshold (99.99, 100.00, 100.01).

## 3. Decision tables
When several conditions combine, enumerate combinations.

| member | coupon valid | total>=100 | expected |
|---|---|---|---|
| Y | Y | Y | member + coupon, capped per rule |
| Y | N | Y | member only |
| N | Y | N | coupon only |
| N | N | N | none |

Use parameterized/table-driven tests (pytest.mark.parametrize, `test.each`, JUnit `@ParameterizedTest`, Go table tests, xUnit `[Theory]`).

## 4. State transitions
For workflows (order: draft→submitted→approved→shipped), test every legal transition, and **every illegal one is rejected without changing state**. AI code frequently allows illegal jumps.

## 5. Property-based testing
Use when the requirement is a rule over many inputs. Common properties:
- **Round trip**: `decode(encode(x)) == x`
- **Idempotence**: `f(f(x)) == f(x)` (normalize, dedupe, retry-safe operations)
- **Invariants**: output never negative; sorted output is a permutation of input; total equals sum of parts
- **Oracle**: compare against a slow, obviously-correct reference implementation written in the test
- **Metamorphic**: changing input in a known way changes output in a known way (adding a zero-priced item does not change total)

Tools: Hypothesis (Python), fast-check (JS/TS), jqwik (Java), FsCheck (.NET), `testing/quick` or rapid (Go), proptest (Rust).

## 6. Error-path and negative testing
For each function: null/None/undefined, empty, wrong type, too large, malformed, duplicates, unauthorized caller, dependency throws/timeouts, partial failure midway. Assert: the correct error type/message/code, no partial writes, resources released, no secret leakage in messages.

## 7. Test doubles
- Fake/stub: clocks, random, network, email/SMS, payment gateways, filesystem, DB (prefer in-memory or containerized real DB for integration tests).
- Do **not** mock: the class under test, value objects, pure helpers, or your own domain logic.
- Verify interactions (`assert_called_with`) only when the interaction *is* the requirement (e.g. "sends exactly one email"). Otherwise assert outcomes.
- A mock that returns whatever the code expects proves nothing; prefer a fake with real behavior, and add a contract test that the fake matches the real dependency.

## 8. Independent oracles
Where does the expected value come from? Rank by trust:
1. Written spec/business owner examples (best)
2. Hand-computed values from the rule
3. Reference implementation or established library/known dataset
4. Existing production behavior (characterization; flag as such)
5. Output of the code under test (never acceptable for new tests)
