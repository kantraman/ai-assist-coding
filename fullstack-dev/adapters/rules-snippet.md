## Full stack development (fullstack-dev)

Apply when building, extending, reviewing, or optimizing a full stack app (database, API, frontend, tests, performance, security) for a given stack. Full instructions: `{SKILL_PATH}/SKILL.md`. Read it first, then open only the reference file the current phase needs (`{SKILL_PATH}/references/`).

Priorities: accuracy and security are hard gates; then testability, maintainability, scalability, performance, flexibility, evolution.

Workflow: 0 intake (infer stack from repo, state assumptions, capture latency/volume/compliance budgets) -> 1 model domain (requirements, entities) -> 2 architecture (modular monolith first) -> 3 database -> 4 API (contract first) -> 5 frontend UX -> 6 implement thin vertical slices, test first -> 7 optimize with measurements -> 8 verify, document, make evolvable.

Techniques, each with a gate:
- Fractal architecture: every module has Contract, Core (pure), Adapters (I/O), Proof (tests + `module.json`). Start 2 levels deep; never add empty layers. Dependencies point downward: ui > api > domain > data > shared.
- Genetic algorithms: only for 3+ interacting measurable tunables with a benchmark (`python3 {SKILL_PATH}/scripts/ga_tuner.py --config <cfg>`). Correctness and security are gates, never objectives. Otherwise run a rubric-scored design tournament of 3 to 5 candidates.
- Knowledge graph + ontology: keep a `module.json` per module; run `python3 {SKILL_PATH}/scripts/kg_build.py validate --root src` and `... impact <module> --root src` before changing shared code.

Non-negotiables: parameterized queries, schema validation at boundaries, server-side object-level authorization, no secrets in code, expand/contract migrations, tests for every requirement. Never invent library APIs or versions; say what you did not run.
