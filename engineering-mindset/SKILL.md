---
name: engineering-mindset
description: Applies a disciplined set of software-reasoning lenses (first-principles, second-order, systems thinking, premortem/inversion, tree-of-thought branching, trade-off matrices, TDD, red-team review, clean code, YAGNI, rubber-duck verification) to design, build, debug, review, or refactor software. Use this skill whenever the user asks for architecture, system design, an implementation plan, code generation, a code review, debugging, a refactor, a technology choice, or "the best way" to build something, even if they never mention thinking styles. Also use when a solution needs to be robust, secure, scalable, maintainable, or when the user wants options and trade-offs rather than a single opinionated answer. Skip only for trivial one-liners or pure syntax questions.
---

# Engineering Mindset

A pipeline of reasoning lenses that turns a software request into a well-reasoned, minimal, tested, and adversarially reviewed solution. The lenses are tools, not a ritual: use the ones the task earns, show only the reasoning that changes a decision.

## Core rules

1. **Proportionality.** Match effort to stakes (see Triage). Ceremony on a small task is a failure, just like skipping rigor on a risky one.
2. **Reasoning must change the output.** If a lens produces nothing that alters the design, code, or recommendation, drop it silently.
3. **Never declare a universal "best."** Every technology or pattern choice is stated as a trade-off against the user's actual constraints.
4. **State assumptions.** When requirements are ambiguous, make the smallest reasonable assumption, state it in one line, and proceed. Ask only when a wrong guess would be expensive.
5. **Verify, don't assert.** Run the code and tests when a sandbox is available. Never claim something works unless it was executed or clearly marked as untested.

## Step 0: Triage

Pick a tier, then run the lenses listed for it.

| Tier | Examples | Lenses |
|---|---|---|
| **Trivial** | rename, one-liner, syntax question | None. Just answer. |
| **Small** | single function, small bug, small script | YAGNI, TDD (a few cases), Clean Code, quick Rubber Duck |
| **Medium** | feature, module, refactor, non-trivial bug | Above + First-Principles, Systems, Red-Team, Second-Order |
| **Large / architectural** | new service, data model, tech selection, migration | All lenses; ToT + Trade-off Matrix + Premortem are mandatory |
| **High-risk** | auth, payments, PII, concurrency, data migration, public API | Large tier + deep Red-Team + Premortem with explicit mitigations and tests per failure mode |

When unsure between two tiers, choose the lower one and escalate if a lens uncovers real risk.

## The pipeline

Phases run in order, but skip or merge any the tier doesn't need. Details, question prompts, and failure modes for each lens are in `references/lenses.md`; ready-made output formats are in `references/templates.md`. Read them when applying a lens in depth.

### Phase 1: Understand (first-principles + systems)
- Restate the real problem in one or two sentences, separated from the proposed solution.
- Reduce to fundamentals: data shape and volume, read/write ratio, latency budget, consistency needs, failure domains, who and what calls this.
- Map the system: components, data flow, trust boundaries, feedback loops (retries, queues, caches, autoscaling), and what this change touches.

### Phase 2: Explore and decide (tree-of-thought + trade-off matrix)
- Generate 2 to 4 genuinely distinct approaches (include the boring baseline).
- Prune obviously dominated options with a one-line reason each.
- Score survivors in a trade-off matrix on axes chosen from the user's constraints (e.g., latency vs. readability, speed to ship vs. operating cost). Weight axes, don't just count.
- Pick one, say why, and name what would make you change the decision.

### Phase 3: Stress the design (inversion + second-order)
- **Premortem:** assume it failed badly in production. List the top failure modes (3 to 7), each with likelihood, impact, detection, and mitigation. Feed mitigations back into the design.
- **Second-order:** for the chosen design and any shortcut, trace consequences at 1 week, 6 months, and 2 years: tech debt, scaling cliffs, team velocity, migration cost, operational burden.

### Phase 4: Scope (YAGNI)
- Cut every feature, abstraction, config option, and dependency not required by a stated requirement or a premortem mitigation.
- Prefer the standard library and existing project dependencies. Every new dependency must justify itself.
- Record deliberate deferrals as one-line "not now" notes instead of building them.

### Phase 5: Tests first (TDD)
- Before logic, write the test list: happy path, boundaries, invalid input, failure/timeout, concurrency, idempotency, and one test per premortem mitigation.
- Write the actual test code when the user wants code. Tests express requirements; the implementation exists to satisfy them.

### Phase 6: Implement (clean code)
- Single responsibility per function/module, intention-revealing names, small functions, low cognitive complexity, no dead code, no speculative generality.
- Explicit error handling, no swallowed exceptions, validated inputs at boundaries, secrets never hardcoded.
- Follow the project's existing conventions over personal preference.

### Phase 7: Attack your own output (red-team)
Switch roles: you are a hostile attacker and a ruthless reviewer. Walk the checklist in `references/templates.md` (injection, authz gaps, unsafe deserialization, SSRF, secrets, prompt-injection points for LLM features, race conditions, resource leaks, unbounded input, error leakage, dependency risk). Fix findings in the code, don't just list them.

### Phase 8: Rubber-duck verify
Explain the code or the debugging trace line by line in plain language, tracking state and assumptions. Any line you cannot justify, or any step that says "this should work", is a suspect. Fix or flag it. For debugging, state the hypothesis, the evidence that would falsify it, and then check, before editing code.

### Phase 9: Deliver
Output only what the reader needs (see Output format).

## Resolving lens conflicts

- **YAGNI vs. premortem/second-order:** YAGNI wins on features and abstractions; the premortem wins on safety. Build the mitigation if the failure is likely or catastrophic, or if retrofitting it later is very expensive (auth boundaries, data schemas, public APIs). Otherwise note it and defer.
- **Clean code vs. performance:** write clear code first; optimize only against a measured or first-principles-justified bottleneck, and comment why.
- **TDD vs. exploration:** for spikes where the shape is unknown, explore first, then write tests before hardening the result.
- **ToT vs. speed:** for reversible, low-stakes decisions, pick the best option after a short mental pass and say it is reversible.

## Debugging variant

Reproduce, then first-principles (what must be true for this symptom?), systems (what else interacts?), ToT over hypotheses ranked by likelihood and cost to test, rubber-duck the trace, write a failing test that captures the bug, fix minimally, run the test, then second-order check (could this fix break something else? is the root cause or only the symptom addressed?).

## Code review variant

Run Red-Team first, then Clean Code, then Systems/Second-Order impact, then test adequacy (TDD lens in reverse: which behaviors are untested?). Report findings by severity with a concrete fix for each.

## Output format

Default to this compact structure and drop sections that add nothing:

1. **Problem and assumptions** (2 to 4 lines)
2. **Decision** (chosen approach, 1 to 2 lines of why, plus a small trade-off matrix when options were genuinely compared)
3. **Risks and mitigations** (premortem table, top items only)
4. **Tests** (list or code)
5. **Implementation** (code)
6. **Review notes** (red-team findings fixed, residual risks, deferred items, what was and wasn't executed)

For small tasks collapse this into a short answer plus code. Never dump every lens's raw output; synthesize.
