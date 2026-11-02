---
name: code-implementation
description: Implements code from software requirements, specifications, user stories, or design docs, one module at a time, starting simple and growing iteratively with the user's feedback. Asks the user how complex and robust the implementation should be, then builds with maintainability, performance, security, scalability and flexibility in mind. Use this skill whenever the user asks to implement, build, code up, or scaffold a feature, service, library, API, or application from a spec or requirements, even if they don't mention modules, quality, or security explicitly. Also use when extending or hardening an earlier implementation.
---

# Code Implementation

Turn requirements into working code, one module at a time. Start with the simplest thing that is correct, then grow it based on what the user wants.

## Workflow

### 1. Understand the spec
Read the requirements. Restate in 3-6 lines what will be built and list any ambiguities. If something blocks correct implementation, ask; otherwise state an assumption and proceed.

### 2. Ask about complexity and robustness (always, before writing code)
Ask in one short message (use the `ask_user_input_v0` tool if available), skipping anything the spec already answers:

- **Complexity target**: Prototype (simplest working) / Standard (clean structure, sensible defaults) / Production-grade (full layering, config, observability).
- **Robustness**: Happy path only / Validates inputs and handles common errors / Defensive (retries, timeouts, idempotency, graceful degradation).
- **Constraints**: language/framework, expected scale, security sensitivity (handles PII, auth, payments?), performance targets.

If the user says "you decide", default to Standard + validated inputs and say so.

### 3. Propose the module breakdown
List modules (name, one-line responsibility, dependencies between them) and the build order, dependencies first. Keep it to what the chosen complexity level needs. Get a quick confirmation unless the user said to proceed.

### 4. Implement module by module
For each module:
1. Write the **simplest correct implementation** at the chosen complexity level.
2. Include tests (or a runnable usage example) proportionate to the level.
3. Give a brief note: what it does, key decisions, what was deliberately left out.
4. Pause for feedback between modules when the project is large; for small ones, continue and summarize at the end.

Run the code and tests when an execution environment is available. Never claim something works without running it.

### 5. Iterate
Build on the previous version according to user input: add features, raise robustness, refactor, optimize. Change only what the request requires; don't rewrite working modules. Offer the next upgrade step ("next I could add X for Y") rather than doing it unasked.

## Quality baseline (apply at every level, cheaply)

- **Maintainability**: small single-purpose functions/modules, clear names, no dead code, comments explain *why*, explicit interfaces between modules.
- **Security**: validate and sanitize external input, parameterized queries, no hardcoded secrets (use env/config), least privilege, no sensitive data in logs, safe defaults, vetted libraries for crypto/auth.
- **Performance**: sensible data structures and algorithms, avoid N+1 queries and needless work in loops; don't optimize speculatively, but flag known hotspots.
- **Scalability**: keep modules stateless where practical, avoid global mutable state, leave seams for caching/queuing rather than building them early.
- **Flexibility**: configuration over hardcoding, dependency injection at module boundaries, extend via interfaces. Don't add abstractions with only one use.

## Scaling the depth to the level

| Aspect | Prototype | Standard | Production-grade |
|---|---|---|---|
| Structure | Few files, minimal layering | Clear modules and interfaces | Layered, config-driven, DI |
| Errors | Fail fast | Validate inputs, meaningful errors | Retries, timeouts, idempotency, structured logging |
| Tests | Smoke test | Unit tests for core logic | Unit + integration, edge cases |
| Security | Baseline above | Baseline + authN/Z where relevant | Threat-model notes, audit logging, rate limiting |
| Docs | Docstrings | README + usage | Architecture notes, runbook |

## Principles

- Simple first. Complexity is added when the user asks for it or the spec requires it, and is named when added.
- Be transparent about assumptions, tradeoffs, and anything skipped.
- Match the project's existing language, style, and conventions when extending code.
- If the user wants a review pass or intent cross-check afterwards, offer it as a follow-up step.
