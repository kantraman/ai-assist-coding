# Lens reference

Contents: Architectural and planning (1 First-Principles, 2 Second-Order, 3 Systems, 4 Inversion) · Execution and coding (5 TDD, 6 Red-Team, 7 Clean Code, 8 YAGNI) · Decision and logic (9 Tree-of-Thought, 10 Trade-off Matrix, 11 Rubber Duck)

## 1. First-Principles Thinking
**Purpose:** strip a problem to physical and logical fundamentals, then build up. Prevents cargo-cult architecture and dependency bloat.
**Ask:**
- What is the actual input, output, and invariant? What is the data's size, shape, growth rate, and lifetime?
- What do CPU, memory, disk, and network cost here (orders of magnitude, not guesses)?
- Which requirement is real, and which is inherited convention ("we always use X")?
- Could a simpler primitive (a file, a hash map, a SQL query, a cron job) do it?
**Output:** a short list of non-negotiable constraints and the simplest design that satisfies them.
**Failure mode:** reinventing solved problems (crypto, parsing, auth). First principles justify what to build, not a license to avoid well-tested libraries for hard domains.

## 2. Second-Order Thinking
**Purpose:** see downstream consequences of a decision.
**Ask:** "And then what?" at 1 week, 6 months, 2 years. Who inherits this? What does this make easier or harder next? What does it lock in (schema, API contract, vendor)? What happens at 10x load or 10x team size?
**Output:** consequence notes per decision, flagging one-way doors (hard to reverse) vs. two-way doors.
**Failure mode:** paralysis. Only trace consequences that are plausible and material.

## 3. Systems Thinking
**Purpose:** reason about relationships, not isolated functions.
**Ask:**
- What are the components, owners, data flows, and trust boundaries?
- What feedback loops exist: retries amplifying load, caches masking staleness, autoscaling lag, queue backlogs?
- Where is state, who owns it, and where can it diverge?
- What are the contracts between parts (APIs, events, schemas) and how do they version?
- What are the bottlenecks and single points of failure?
**Output:** a small component/flow description (text or diagram) with the change's blast radius.
**Failure mode:** boiling the ocean. Map only what the change can affect.

## 4. Inversion Thinking (Premortem)
**Purpose:** design backwards from failure.
**Method:** "It is six months from now and this failed spectacularly. Why?" Cover: data loss/corruption, outage, security breach, runaway cost, silent wrong results, performance cliff, operational confusion, failed migration/rollback, dependency or vendor failure, human error.
**Output:** failure-mode table (see templates). Each high-impact row yields a design change, a test, or a monitoring signal.
**Failure mode:** listing exotic risks while missing the mundane (timeouts, null input, partial failure, retries without idempotency).

## 5. Test-Driven Thinking
**Purpose:** requirements become executable before the solution exists.
**Method:** derive tests from behavior, not implementation. Cover: happy path; boundaries (0, 1, max, off-by-one, empty, unicode, huge); invalid and hostile input; dependency failure, timeout, partial failure; concurrency and idempotency (double submit, retry); time (timezones, DST, clock skew); one test per premortem mitigation; regression test for every bug fixed.
**Output:** a test list (names as behavior sentences) and, when asked for code, runnable tests written before the logic.
**Failure mode:** testing implementation details, mocking everything so tests prove nothing, snapshot tests that approve bugs.

## 6. Red-Team / Adversarial Thinking
**Purpose:** find flaws in your own output before someone else does.
**Method:** switch persona to attacker, then to merciless reviewer. Attack each trust boundary and each piece of untrusted input. See the checklist in templates.md.
**Output:** findings with severity and a concrete fix, applied to the code.
**Failure mode:** generic checklist recitation. Tie every finding to a specific line or flow.
**Note:** this is defensive review of code being written. Do not produce working exploits against third-party systems.

## 7. Clean Code / Refactoring
**Purpose:** code humans can change safely.
**Rules of thumb:** one reason to change per unit (SRP); names that state intent; functions that do one thing at one level of abstraction; few parameters; no flag arguments; early returns over deep nesting; cognitive complexity low; remove duplication only when it represents the same concept (rule of three); delete dead code and stale comments; comments explain why, not what.
**Smells to hunt:** long method, god class, feature envy, shotgun surgery, primitive obsession, speculative generality, magic numbers, hidden temporal coupling.
**Refactoring safety:** refactor only under green tests; small steps; behavior preserved.
**Failure mode:** over-abstracting in the name of cleanliness, which collides with YAGNI.

## 8. Extreme Minimalism (YAGNI)
**Purpose:** the best code is the code not written.
**Method:** for every element ask "Which stated requirement needs this?" Remove unused configurability, plugin systems, interfaces with one implementation, generic frameworks, premature caching/sharding/microservices, and dependencies replaceable by a few lines.
**Exception:** keep what is cheap now and ruinous to retrofit (security boundaries, schema constraints, API versioning, observability hooks), as justified by the premortem.
**Output:** a "deferred" list instead of speculative code.

## 9. Tree-of-Thought / Branching
**Purpose:** compare real alternatives before committing.
**Method:** branch into 2 to 4 distinct approaches (different in structure, not wording). Expand each just enough to see its fatal flaw or its strengths. Prune with explicit reasons. Backtrack if the leading branch fails a constraint. Include the simplest baseline.
**Output:** surviving options carried to the matrix; pruned options with one-line reasons.
**Failure mode:** fake branches that are the same idea reworded, or branching so wide nothing gets evaluated.

## 10. Trade-off Matrix
**Purpose:** replace "X is best" with explicit, constraint-driven comparison.
**Method:** choose 4 to 7 axes from the user's context (latency, throughput, correctness/consistency, readability, dev speed, operating cost, team familiarity, security, portability, reversibility). Weight them. Score each option with a brief justification, not just numbers. State the winner under these weights and how the winner changes if weights change.
**Failure mode:** false precision. Scores are judgments; show the reasoning and the sensitivity.

## 11. Rubber Duck Debugging
**Purpose:** expose faulty assumptions by explaining plainly.
**Method:** narrate the code or trace step by step: what each line does, what state is true before and after, and why. Flag phrases like "should", "probably", "obviously". For bugs: hypothesis, prediction, evidence, conclusion.
**Output:** corrections made, plus assumptions that remain unverified.
**Failure mode:** narrating what you intended rather than what the code actually does. Trace the real values.
