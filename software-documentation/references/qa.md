# QA tester documentation

Goal: a tester who has never seen the project can set up, know what to test, know what "correct" looks like, execute the tests, and report bugs in a form developers can act on.

The most important rule: **expected results must come from a source** (spec, code, acceptance criteria, user statement). A test case whose expected result is a guess teaches testers the wrong behaviour. If the correct behaviour is unclear, write the case with `Expected: TBC` and add it to open questions for the PM or BE lead.

Documenting tests is not running them. Never state or imply that tests passed, and do not fabricate execution results. Leave the result columns empty for the tester to fill in.

## Contents
1. Document set
2. Test plan template
3. Test environment and data guide
4. Feature-to-test coverage map
5. Test case template and how to derive cases
6. API test cases (with Postman)
7. Regression and smoke suites
8. Known issues, limitations and out-of-scope
9. Bug report template and severity scale
10. UAT script (for client acceptance)
11. Release sign-off
12. Worked example

---

## 1. Document set

| Document | Purpose |
|---|---|
| Test plan | Scope, approach, environments, entry/exit criteria, risks |
| Environment and test-data guide | How to get a working test setup, accounts, seed data, reset |
| Coverage map | Which feature/requirement is covered by which test cases |
| Test cases (functional, API, negative, permissions, non-functional) | Executable steps with expected results |
| Smoke and regression checklists | Short suites to run on every build / release |
| Known issues and limitations | So testers do not log intended behaviour as bugs |
| Bug report template + severity scale | Consistent defect reporting |
| UAT script (if client acceptance is needed) | Plain-language scenarios for the client to sign off |
| Sign-off sheet | Release decision record |

Produce only what was asked. For "QA documentation" with no detail, produce plan, environment guide, coverage map, test cases, smoke checklist, known issues and the bug template.

## 2. Test plan template

```markdown
# <Product> - Test Plan
Version | Date | Build/release under test | Author | Sources used

## 1. Objective
What this test cycle must establish, in 2-3 sentences.

## 2. Scope
**In scope:** features, platforms, integrations, API versions.
**Out of scope:** and why (not delivered, third-party owned, covered elsewhere).

## 3. Test approach
Test types and the intent of each: functional, API, integration, regression, permissions/roles,
validation and boundary, usability, compatibility (browsers/devices/OS versions), performance,
security basics, accessibility. Mark each as In / Out for this cycle.
Manual vs automated: which cases are automated, where they live, how to run them.

## 4. Environments and builds
Which environment tests run on, how builds are deployed to it, how testers learn what build they are on (version endpoint, footer text, commit hash).

## 5. Entry criteria
e.g. build deployed, smoke suite passes, test data seeded, known blockers listed.

## 6. Exit criteria
e.g. all critical/high cases executed, no open Critical/High defects, agreed pass rate, all open Medium defects triaged.
Use the numbers the team agreed; if none, propose and mark as "proposed".

## 7. Risks and dependencies
Third-party sandboxes, unstable environments, missing data, features behind flags, unclear requirements.

## 8. Roles and communication
Who tests, who triages, where bugs are logged, how blockers are escalated.

## 9. Schedule
Only if the user provides dates. Do not invent a timeline.
```

## 3. Test environment and data guide

Cover everything needed to start testing within 30 minutes:

- **Access:** URLs per environment, VPN or allow-list needs, how to request access. Never include real credentials; state where test credentials are held.
- **Test accounts:** one row per role - role, purpose, username pattern, how to get the password (placeholder).
- **Seed data:** what data exists, how to load it, and how to reset to a clean state.
- **Feature flags and config** that change behaviour and must be set a certain way for testing.
- **Third-party sandboxes:** payment test card numbers, email catchers, SMS stubs, with the vendor's official test values only when you can verify them from the code/config or the vendor docs the user supplied.
- **Time-dependent behaviour:** how to test expirations, scheduled jobs, and timezone effects (e.g. shortened expiry in test config).
- **Tools:** Postman collection and environment (see `postman.md`), browser dev tools tips, log access, DB read access if applicable.
- **Build identification:** how to confirm the build under test.

## 4. Coverage map

Rows are requirements or features; columns show the test cases that cover them. Gaps are visible at a glance.

| Req / feature | Description | Test case IDs | Type | Coverage |
|---|---|---|---|---|
| REQ-12 | Customer can cancel an unshipped order | TC-ORD-014, TC-ORD-015, TC-ORD-016 | Functional, Negative | Full |
| REQ-13 | Admin can refund a cancelled order | - | - | **None - needs cases** |

Coverage values: Full / Partial / None / Not testable (say why). Derive the feature list from the same sources as the other docs (routes, screens, tickets) so all documents agree.

## 5. Test case template and how to derive cases

### Template

```markdown
**TC-<AREA>-<nnn>: <short title stating the behaviour under test>**
Priority: P1 | P2 | P3     Type: Functional | Negative | Boundary | Permission | API | UI | Compat | Perf | Security
Requirement: <ID or feature>
Preconditions: <data/state/role required>
Test data: <exact values>

| Step | Action | Expected result |
|---|---|---|
| 1 | ... | ... |

Result: ____   Build: ____   Tester: ____   Date: ____   Bug ID: ____
```

For large suites, use a table with one row per case (ID, title, preconditions, steps, expected, priority, type, result) so it can be exported to a spreadsheet; offer an Excel version via the xlsx skill if the team will track execution in a sheet.

### Writing good cases
- One behaviour per case; the title states what is verified ("Cancel is rejected after shipment"), not "Test cancel".
- Steps are exact and repeatable by someone unfamiliar with the product. Use the product's exact UI labels and real test values.
- Expected results are observable: what message text, status, field value, redirect, email, or record change appears. Include side effects (email sent, stock restored, audit entry).
- State preconditions explicitly, including role and data state.
- Give priority by business impact: P1 = core flow or data/money/security risk; P2 = important feature; P3 = minor or cosmetic.

### Deriving cases systematically
Work through the sources and produce cases from each lens, so nothing relies on intuition alone:

| Lens | Source to read | Cases to write |
|---|---|---|
| Happy path | Requirements, user flows | One per main flow, end to end |
| Validation | Validators, schema constraints | Each rule: valid, just-invalid, missing, wrong type, too long, special characters |
| Boundaries | Limits in code/config | min, min-1, max, max+1 for lengths, quantities, page sizes, file sizes, dates |
| State transitions | State machines, status enums | Every allowed transition and representative disallowed ones |
| Permissions | Auth middleware, role checks | Each role x action: allowed and denied; unauthenticated; expired session |
| Error handling | Error catalogue, catch blocks | Each documented error is triggerable and shows the right message |
| Data integrity | Models, constraints | Duplicates, uniqueness, cascade/delete behaviour, concurrent edits |
| Integration | Third-party calls | Success, failure, timeout, retry, duplicate callback |
| Idempotency/retry | Idempotency keys, retries | Same request twice, double-click, refresh after submit |
| Empty/large | Lists, reports | Zero records, one record, many records, pagination edges |
| Localisation/time | Date/time/currency code | Timezones, DST, locale formats, long text, unicode |
| UI states | Components | Loading, empty, error, disabled, responsive breakpoints |
| Non-functional | Config, stated requirements | Performance targets, accessibility basics, browser/device matrix - only where requirements exist |

## 6. API test cases (with Postman)

For API work, pair the written cases with the generated Postman collection (`postman.md`):

- Each endpoint gets at least: one success case, one validation failure, one auth failure (no token, wrong role), and each documented error code.
- Reference the Postman request name in the case ("Postman: Orders > Create order") so a tester can run it in one click.
- Specify exact request data and the expected status, response body fields, and side effects, plus response-time expectation if one exists.
- Include sequencing flows (create -> read -> update -> delete) as scenarios; point to the workflow folder in the collection.
- Note which cases are covered by the collection's automatic tests (status, JSON type, required fields) so testers know what still needs manual verification (business correctness, side effects).

```markdown
**TC-API-007: Create order is rejected when stock is insufficient**
Priority: P1   Type: API, Negative   Requirement: REQ-04
Preconditions: Item SKU-100 has stock 2; caller authenticated as `customer`; cart contains 3 x SKU-100
Postman: Orders > Create order (change quantity in cart first)

| Step | Action | Expected result |
|---|---|---|
| 1 | POST /v1/orders with cartId of the prepared cart | 409, body code `INSUFFICIENT_STOCK`, `details.items` lists SKU-100 |
| 2 | GET /v1/items/SKU-100 | stock is still 2 (nothing reserved) |
```

## 7. Regression and smoke suites

- **Smoke suite (10-20 minutes):** the shortest path proving the build is testable: app loads, login works, one core create/read flow, one API health check, critical integrations reachable. If smoke fails, testing stops and the build is rejected.
- **Regression suite:** all P1 cases plus P2 cases for areas touched by recent changes. Organise by area and state the trigger ("run in full before every release; run area X when module X changes").
- Present as a checklist table: ID, check, pass/fail, notes. Link each item to its full test case.

## 8. Known issues, limitations and out-of-scope

Prevents wasted bug reports. Table: Item | Behaviour | Intended/Defect | Ticket | Workaround.
Include: features disabled by flag, third-party sandbox quirks, accepted limitations from the PM doc, platforms not supported. Pull from the client and PM documents so all three agree; do not invent entries.

## 9. Bug report template and severity scale

```markdown
**Title:** <component> - <what is wrong> (<condition>)
**Environment / build:** 
**Role / account used:** 
**Preconditions / data:** 
**Steps to reproduce:** 1... 2... 3...
**Expected result:** (cite the requirement or doc section)
**Actual result:** 
**Frequency:** always | intermittent (x of y)
**Evidence:** screenshot / video / HAR / console error / API request+response / log excerpt with timestamp and request ID
**Severity:** Critical | High | Medium | Low
**Priority (suggested):** 
**Workaround:** 
**Related test case / requirement:** 
```

Severity scale (adapt to the team's existing one, if any):

| Severity | Definition | Example |
|---|---|---|
| Critical | Data loss, security breach, payment error, system down, no workaround | Orders charged twice |
| High | Core feature broken or blocked, workaround is difficult | Cannot complete checkout on mobile |
| Medium | Feature partly broken, reasonable workaround | Filter ignores date range, manual sort works |
| Low | Cosmetic or minor inconvenience | Misaligned label, typo |

Add a short "good vs bad bug report" example: a good title is "Checkout - 500 error when applying expired coupon (guest user)"; a bad one is "Coupon broken".

## 10. UAT script (client acceptance)

Plain language, scenario-based, no technical terms. One scenario per business outcome:

```markdown
### UAT-03: Customer cancels an order before it ships
**Role:** Customer     **Estimated time:** 5 minutes
**You need:** An order with status "Processing" (test order provided: ORDER-TEST-1)
1. Sign in as the test customer.
2. Open **My orders** and select ORDER-TEST-1.
3. Click **Cancel order** and confirm.
**Expected:** The order shows status **Cancelled** and a confirmation email arrives.
**Result:** Pass / Fail     **Comments:**
```

Close with acceptance criteria and a signature block (name, role, date, decision: Accepted / Accepted with conditions / Rejected, conditions listed).

## 11. Release sign-off

| Check | Status | Evidence / link |
|---|---|---|
| Smoke suite passed on release build | | |
| All P1 cases executed and passed | | |
| Open defects by severity (C/H/M/L) | | |
| Known issues documented | | |
| Regression suite executed | | |
| UAT accepted (if applicable) | | |
| Decision: Go / No-go | | |

Leave status cells blank for the team to complete.

## 12. Worked example (validation case with boundaries)

```markdown
**TC-USR-021: Username length boundaries are enforced at registration**
Priority: P2   Type: Boundary, Functional   Requirement: REQ-02 (username 3-20 chars)
Preconditions: Registration page open; usernames below are unused

| Step | Test data | Expected result |
|---|---|---|
| 1 | `ab` (2 chars) | Field error: "Username must be 3-20 characters"; no account created |
| 2 | `abc` (3 chars) | Account created |
| 3 | `a` x 20 | Account created |
| 4 | `a` x 21 | Field error as in step 1; no account created |
| 5 | empty | Field error: "Username is required" |
```
(If the messages above could not be confirmed from the code or spec, write them as `TBC` and ask for the correct text.)
