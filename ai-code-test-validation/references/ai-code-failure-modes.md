# AI-Generated Code: Common Failure Modes and Tests That Catch Them

## Contents
- Requirement-level failures
- Logic failures
- Robustness failures
- Integration/API failures
- Security failures
- Test-level failures (when AI also wrote the tests)
- Review checklist

## Requirement-level failures
| Failure | Test that catches it |
|---|---|
| Plausible but wrong interpretation of an ambiguous requirement | Test from written examples in the spec; list the ambiguity in the report |
| Missing requirement (feature silently omitted) | Traceability matrix: any requirement with no test is a finding |
| Extra behavior nobody asked for (extra fields, side effects, logging PII) | Negative assertions: output has exactly the expected shape; no unexpected calls/writes |
| Ignored business edge rules (rounding, currency, time zone, locale) | Boundary tests with real-world values (0.005 rounding, DST day, non-ASCII names) |

## Logic failures
| Failure | Test |
|---|---|
| Off-by-one, `<` vs `<=` | Boundary triplets T-1, T, T+1 |
| Wrong operator precedence / inverted condition | Decision table covering every combination |
| Float arithmetic for money | Sum of 0.1+0.2 style cases; use decimal/integer cents assertions |
| Mutable default arguments / shared state (Python), shared references | Call twice; assert second call is unaffected |
| Copy vs reference bugs | Mutate the input after the call; assert result unchanged |
| Sorting/stability/locale assumptions | Duplicates, ties, mixed case, unicode |
| Incorrect date math (month length, leap year, UTC vs local) | Feb 29, Dec 31→Jan 1, DST transitions, negative offsets |
| Integer overflow / large inputs | Max values, 10^6 element input, timing sanity |

## Robustness failures
| Failure | Test |
|---|---|
| Swallowed exceptions / bare `except` / empty `catch` returning defaults | Force dependency to throw; assert error surfaces correctly |
| Missing null/empty handling | None, "", [], {} for every parameter |
| No input validation | Wrong types, negative numbers, oversized strings, injection strings |
| Resource leaks (files, connections, goroutines, subscriptions) | Assert close/cleanup called on success **and** failure paths |
| Partial failure leaves inconsistent state | Fail on step 2 of 3; assert rollback or no partial write |
| Non-idempotent retries / double submit | Call twice with the same request id; assert single effect |
| Race conditions | Concurrent calls (threads/async), run repeatedly; use race detector where available |
| N+1 queries / unbounded loops | Count queries or calls for N=1 vs N=100 |

## Integration/API failures
| Failure | Test |
|---|---|
| **Hallucinated APIs**: calls to functions, methods, parameters or library versions that don't exist | Import/compile everything; run at least one real (unmocked) call into each third-party library used; do not mock the library away in every test |
| Wrong HTTP status/error format | Contract test on status codes, headers, error body shape |
| Wrong serialization (field names, casing, date format, null vs missing) | Schema validation against OpenAPI/JSON Schema; round-trip tests |
| Misuse of async (missing await, unhandled promise, blocking call in event loop) | Async tests that await; assert rejected promises are handled |
| Deprecated/insecure library usage | Static analysis + lint in CI (report, don't just test) |

## Security failures
| Failure | Test |
|---|---|
| Missing authorization check | Call as unauthenticated, wrong role, other tenant's user; expect 401/403 and no data |
| SQL/command/template injection | Payloads like `' OR 1=1--`, `; rm -rf`, `{{7*7}}`; assert treated as data |
| Path traversal | `../../etc/passwd`, absolute paths, symlinks |
| Secrets in logs/errors | Capture logs/exception text; assert no tokens/passwords |
| Insecure defaults (weak hashing, no expiry) | Assert algorithm/params/expiry explicitly |

## Test-level failures (when AI also wrote the tests)
Recognize and refuse these in your own output and flag them in reviews:
- **Tautology**: expected value computed with the same logic as the implementation
- **Snapshot of current output** treated as truth
- **Assert-nothing tests** (no assertion, or only "does not throw")
- **Over-mocking**: everything is mocked, so the test exercises only the mocks
- **Happy-path only** with one or two examples
- **Test asserts the bug**: incorrect current behavior locked in as expected
- **Coverage padding**: lines executed, nothing checked
- **Order/time dependence** and shared state between tests
- **Loosened assertions** to get green after a failure

## Review checklist (use when auditing existing AI-written tests)
1. Can I name the requirement each test protects?
2. If I flip one operator in the code, does a test fail?
3. Are expected values independent of the implementation?
4. Are error paths and boundaries tested, not just the happy path?
5. Is anything mocked that should be real?
6. Would the suite catch a hallucinated or misused library call?
7. Any flaky or order-dependent tests (run 3x, shuffled)?
