# Requirement Traceability Matrix

| ID | Requirement (testable statement) | Source | Type | Tests | Negative/edge tests | Mutation-killed? | Status |
|----|----------------------------------|--------|------|-------|---------------------|------------------|--------|
| R1 | Given ..., when ..., then ... | ticket #123 / spec §4 / user | explicit | test_x | test_x_boundary | yes / no / n/a | covered |
| R2 | ... | inferred from docstring | **inferred** | | | | **needs confirmation** |

**Status values**: covered · partially covered · not covered · blocked (needs clarification) · defect found

## Implicit rules checked
- [ ] Rounding / currency precision
- [ ] Time zones / DST / locale
- [ ] AuthN / AuthZ / tenant isolation
- [ ] Input validation and error messages
- [ ] Idempotency / retries / concurrency
- [ ] Ordering / pagination limits
- [ ] Audit logging / no sensitive data in logs

## Defects found in code under test
| Test | Requirement | Expected | Actual | Severity |
|------|-------------|----------|--------|----------|

## Assumptions and open questions
1.
