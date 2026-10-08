---
name: ai-code-test-validation
description: Design and write unit tests and regression tests that genuinely validate code (especially AI-generated code) against business requirements, adapting to the project's language, framework and conventions. Use whenever the user asks to write, generate, improve, review or audit unit tests, regression tests, test suites, test coverage, or asks "is this AI-written code correct/good enough/safe to merge", "does this meet the requirements", "add tests for this change/bug fix", or wants QA validation of generated code. Trigger even if the user only says "test this" or "add coverage" and even if they do not name a language or framework. Primary stacks are JavaScript/TypeScript (Node, NestJS, React, Angular), Python (pytest, FastAPI, Django), C# / ASP.NET Core, and Java Spring Boot; also handles Go, Rust and others.
---

# AI Code Test Validation

Write tests that can actually **fail when the code is wrong**. AI-generated code usually compiles, runs, and passes AI-generated tests, and is still wrong, because both sides share the same misunderstanding. Your job is to break that loop: derive tests from the *requirements*, not from the implementation, and then prove the tests have teeth.

## Core principles (and why)

1. **Requirements are the oracle, code is the suspect.** A test derived by reading the implementation only confirms what the code does, not what it should do. Always start from the business requirement, acceptance criteria, ticket, docstring, API contract, or user description. If none exists, say so, state the assumed behavior explicitly, and get it confirmed (see "No requirements available").
2. **A test that cannot fail is worthless.** Every suite you deliver must survive a mutation check (Step 6): deliberately break the code and confirm tests go red.
3. **Fit the codebase, don't impose on it.** Use the project's existing runner, assertion style, naming, fixtures and folder layout. Introduce new tooling only when the user agrees.
4. **Traceability beats coverage.** 100% line coverage with no requirement mapping proves little. Every requirement should map to at least one test, and every test to a requirement or a stated risk.
5. **Be honest about gaps.** Report what is untested, what was assumed, and what could not be verified.

## Workflow

Follow these steps in order. Scale effort to the size of the change: a 20-line function does not need a 10-page test plan, but it still needs Steps 1, 2, 4, and 6.

### Step 1 — Discover the stack and conventions

Run the detector to get language, frameworks, test runner, and commands:

```bash
python /path/to/skill/scripts/detect_stack.py <project_root>
```

Then read 2–3 existing test files to learn naming, fixture, mocking, and assertion style. Read the per-language reference **before writing any test**:

| Detected | Read |
|---|---|
| `.py`, pyproject, pytest, FastAPI/Django/Flask | `references/python.md` |
| `.js/.ts/.tsx`, package.json, Node/NestJS/React/Angular | `references/javascript-typescript.md` |
| `.cs`, `.csproj`, ASP.NET Core | `references/dotnet.md` |
| `.java`, pom.xml, build.gradle, Spring Boot | `references/java-kotlin.md` **and** `references/spring-boot.md` |
| `.go` / `.rs` | `references/go.md` / `references/rust.md` |
| Anything else | Use `references/techniques.md` and translate idioms to the local runner |

Multi-language repos (e.g. Spring Boot API + React front end): read each relevant reference and test each layer with its own runner. Contract tests between the layers (API schema, error format) are where AI-generated front and back ends most often disagree.

Confirm the test command actually runs on the *unmodified* project first. If the baseline is already red, report that before proceeding.

### Step 2 — Extract requirements into a traceability matrix

Collect requirements from (in priority order): user's stated requirements, tickets/specs/PRD/README, API schemas (OpenAPI, GraphQL, protobuf), docstrings and comments, existing tests, then the code itself (lowest trust). Write them as numbered, testable statements:

```
R1  Given a cart with items totalling >= $100, a 10% discount is applied to the subtotal.
R2  Discount never applies to gift cards.
R3  Invalid coupon returns error CODE_INVALID and leaves the cart unchanged.
```

Use `assets/traceability_template.md` as the format. Mark each requirement **explicit** (stated by user/spec) or **inferred** (you deduced it). Inferred ones must be flagged in the final report.

Also list **implicit business rules** that generated code often misses: rounding and currency precision, time zones, authorization, idempotency, ordering, pagination limits, data retention, audit logging, error messages the user sees.

### Step 3 — Design the test plan (before writing code)

For each requirement, choose techniques from `references/techniques.md`: equivalence partitioning, boundary values, decision tables, state transitions, property-based tests, error-path and negative tests. Then add **risk-based tests** from `references/ai-code-failure-modes.md` (hallucinated APIs, off-by-one, swallowed exceptions, mutable defaults, missing validation, N+1, resource leaks, and so on).

A good plan for each unit lists: happy path, boundaries, invalid input, empty/null/huge input, error propagation, and side effects (what must NOT change).

### Step 4 — Write the unit tests

Rules that keep tests honest:

- **Assert on observable behavior** (return values, state changes, emitted events, calls to real boundaries), not on internal implementation details.
- **Compute expected values independently**, by hand or from the spec. Never copy the function's logic into the test, and never generate the expected value by running the code under test and pasting the output.
- **One reason to fail per test**, with names that read as requirements: `test_gift_cards_are_excluded_from_discount`.
- **Mock only true boundaries** (network, clock, filesystem, DB, randomness, third-party services). Do not mock the unit under test or its pure collaborators; over-mocking makes tests pass regardless of correctness.
- **Assert specifics.** `assert result` and `expect(x).toBeTruthy()` pass for many wrong answers. Assert exact values, exact error types and messages, exact call arguments.
- **Deterministic and isolated**: freeze time, seed randomness, no shared mutable state, no order dependence.
- **Cover negative space**: assert that things that should not happen do not happen (no discount on gift cards, no write on validation failure).
- Add **property-based** tests where the requirement is a general rule (round-trips, idempotency, ordering invariants, "never negative").

### Step 5 — Write the regression tests

Regression tests protect behavior that must not change. Pick the right kind (details in `references/regression.md`):

- **Bug-repro test**: for each fixed bug, write the test *first*, confirm it fails on the buggy code, then passes on the fix.
- **Characterization test**: for legacy or untested code being modified or replaced by AI, pin the current behavior at the public interface before changing anything. Mark quirks you believe are bugs rather than silently blessing them.
- **Contract test**: pin public API shapes, schemas, error codes, and serialized formats that other systems depend on.
- **Golden/snapshot test**: only for large structured outputs; review diffs by hand and never auto-update snapshots to make the suite green.
- **Critical-path integration test**: a small number of end-to-end flows for the money/security/data-loss paths.

Tag or group regression tests so they can run in CI separately (e.g. markers, tags, categories).

### Step 6 — Prove the tests have teeth (validation of the tests)

Do not skip this. It is what makes the suite a real quality gate.

1. **Run the suite** and confirm green on the code under test. Run it 3 times (or with random order) to detect flakiness.
2. **Coverage**: measure line *and branch* coverage. Inspect uncovered branches; each is either untested behavior (add a test) or dead code (report it).
3. **Mutation check**. Preferred: the ecosystem's tool (mutmut/cosmic-ray, Stryker, PIT, Stryker.NET; see the language reference). If a tool is unavailable or the network is off, use the bundled runner, which works for every language above:

   ```bash
   python /path/to/skill/scripts/mutate.py --file <source file> \
       --test-cmd "<fast test command scoped to that module>" \
       [--build-cmd "<compile command>"]   # required for Java/C#/Rust/Go so non-compiling mutants are ignored
   ```

   It applies one small bug at a time (flip `>=`, `==`, `&&`, `+`, booleans, off-by-one literals), runs your tests, always restores the file, and re-runs the suite at the end to confirm the project is clean. Every **survivor** is a missing or weak test: write the test from the requirement (not from the mutant), re-run, and repeat until the survivors are killed or shown to be equivalent (behavior-identical) mutants. Scope to the changed file(s) and a fast test command; aim for 80%+ on business-logic code, 100% on money/security rules. It only mutates operators and literals, so also do a short manual pass for what it cannot do: deleting a validation, removing a side effect, swallowing an exception, changing a default.
   See `references/worked-example.md` for a real weak-vs-strong comparison.
4. **Requirement check**: walk the traceability matrix; every requirement must have a passing test that would fail if the requirement were violated.

Record results in the report. A suite that passes but has survivors you could not kill must be reported as such.

### Step 7 — Report

Deliver the tests plus a short report:

```
## Verdict: [READY / READY WITH GAPS / NOT READY]
Stack: <language, framework, runner, command>
Tests added: N unit, N regression (files listed)
Requirements coverage: X of Y mapped (table in appendix)
Coverage: line %, branch %
Mutation check: killed K of M mutants (tool or manual); survivors: ...
Defects found in the code under test: (with failing test names)
Assumptions / inferred requirements needing confirmation:
Not tested / known gaps:
How to run: <commands>
```

If a test fails against the AI-generated code because the code violates a requirement, **do not weaken the test to make it pass.** Report the defect, show the failing test, and (if asked) propose or apply the fix in the code.

## No requirements available

Do not invent business rules silently. Do this instead: (1) derive candidate rules from names, docstrings, callers, and existing tests; (2) list them as inferred requirements; (3) ask the user to confirm the few that are ambiguous or high-impact (money, permissions, data deletion); (4) write tests for confirmed and low-risk ones, and mark the rest clearly in the report. Ask at most a handful of questions in a single message.

## Ground rules on the environment

- Use only dependencies already in the project unless the user approves adding more. When suggesting new dev dependencies (mutation tools, property-based libraries), name them and explain why.
- If the network is disabled you cannot install packages; fall back to the manual mutation pass and stdlib-based tests.
- Never modify production code to make tests easier to write without saying so; if testability requires a change (dependency injection, clock parameter), propose it and keep the change minimal.
- Do not delete or loosen existing tests. If an existing test is wrong, flag it and explain.
- Never include real secrets, PII, or production data in fixtures.

## Reference index

- `references/techniques.md` — test design techniques with examples
- `references/ai-code-failure-modes.md` — what AI-generated code gets wrong and the test that catches each
- `references/regression.md` — regression strategies in depth
- `references/python.md`, `javascript-typescript.md`, `dotnet.md`, `java-kotlin.md`, `spring-boot.md` — primary stacks: runners, slices, mocking, property-based and mutation tooling, framework pitfalls
- `references/go.md`, `rust.md` — secondary stacks
- `references/worked-example.md` — weak vs requirement-driven suite, with mutation scores
- `assets/traceability_template.md` — requirement-to-test matrix
- `scripts/detect_stack.py` — stack and test-command detection
- `scripts/mutate.py` — language-agnostic mutation check with safe restore
