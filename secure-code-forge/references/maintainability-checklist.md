# Maintainability Checklist

## Structure
- One responsibility per function/module; functions fit on a screen (~40 lines as a smell threshold), ≤ 4-5 parameters (group into objects beyond that).
- Nesting depth ≤ 3; use early returns/guard clauses.
- Cyclomatic complexity ≲ 10 per function; split when higher.
- Business logic separated from I/O, framework glue, and configuration; side effects at the edges.
- No duplicated logic (rule of three); no god classes or utility dumping grounds.

## Clarity
- Names reveal intent; avoid abbreviations and boolean flag parameters that change behavior.
- Types/annotations on public interfaces (type hints, TypeScript types, generics).
- Comments explain *why* and constraints/assumptions; docstrings on public API with inputs, outputs, errors.
- No magic numbers; named constants with units.
- No dead code, commented-out blocks, or unused imports/variables.

## Error handling
- Never swallow errors (`except: pass`, empty `catch`). Catch narrowly; add context; re-raise or convert to domain errors.
- Resource cleanup via context managers / `finally` / `defer` / RAII.
- Fail fast on invalid state with clear messages.

## Testability
- Dependencies injected (clock, DB, HTTP) so tests don't need the network.
- Tests cover each requirement, edge cases (empty, max, boundary, unicode), and failure paths; security-negative tests for hostile input and unauthorized access.
- Deterministic tests: no sleeps on real time, no dependence on ordering or external state.

## Operability
- Structured logging with levels and correlation ids; no secrets in logs.
- Configuration via environment/config files with validation at startup; sane defaults.
- Pinned dependencies and a lockfile; README with setup, run, test commands.
- Backward-compatible changes to public interfaces, or explicit versioning.
