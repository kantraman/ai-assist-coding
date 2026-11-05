---
name: fullstack-dev
description: Build, extend, or review full stack applications for a given tech stack, covering database schema design, API design, frontend UI/UX design from scratch, testing, security, and performance. Uses fractal (self-similar) modular architecture, genetic-algorithm optimization of measurable tunables, and a knowledge graph with an ontology to track relationships between modules. Use this skill whenever the user names a stack (Next.js, Django, FastAPI, Spring, Rails, Laravel, NestJS, .NET, Go, React, Vue, Angular, Postgres, etc.) and wants an app, feature, backend plus frontend, schema, REST/GraphQL API, or UI built, scaled, optimized, refactored, or architected, even if they never say "full stack". Also use for requests about modular architecture, dependency graphs between modules, schema or index tuning, or evolving an existing codebase safely.
---

# Full Stack Developer

Turn a tech stack plus a goal into a working, tested, secure, evolvable application: data model, API, UI, and the glue between them.

Three techniques give this skill its edge. Each has a specific job, and each has a gate that stops it from becoming decoration:

| Technique | Job | Gate (when NOT to use it) |
|---|---|---|
| **Fractal architecture** | One repeating shape (Contract, Core, Adapters, Proof) at every scale so the codebase stays predictable as it grows | Tiny apps: stop at 2 levels. Never create empty layers |
| **Genetic algorithms (GA)** | Search combinatorial design/tuning spaces against a measurable fitness (index sets, cache sizes, pool sizes, chunking, query variants) | Needs a benchmark and at least 3 interacting tunables. Otherwise use a rubric-scored design tournament, or just measure and pick |
| **Knowledge graph + ontology** | Typed relationships between requirements, modules, entities, endpoints, components, tests, risks, so impact analysis and drift checks are mechanical | Skip graph maintenance for throwaway scripts |

Priorities, in the order they break ties: **accuracy, security, testability, maintainability, scalability, performance, flexibility, evolution**. Accuracy and security are gates; the rest are optimized. Performance work never trades away correctness.

## Workflow

Work through the phases in order, but size the effort to the task. A single endpoint needs phases 1, 4, 6, 8 in miniature; a greenfield app needs all of them.

### Phase 0: Intake (stack profile)
Establish the stack, the goal, and non-functional budgets. Infer from the repo (package.json, pyproject.toml, pom.xml, go.mod, Gemfile, composer.json) before asking. Ask only for what is missing and would change the design; otherwise state assumptions in one line and proceed. Record a **Stack Profile**; see `references/stack-profiles.md` for fields and per-stack defaults. If you can browse or search the web, verify current stable versions and breaking changes before pinning dependencies, because training knowledge goes stale.

Capture budgets early (they become fitness functions later): target p95 latency, expected users and data volume, availability, compliance (PII, payments, health), team size.

### Phase 1: Model the domain and start the graph
List requirements as short testable statements (R1, R2...). Extract entities and their relationships. Seed the knowledge graph: requirements, entities, modules. See `references/knowledge-graph-ontology.md`.

### Phase 2: Architecture, fractally
Pick the smallest decomposition that fits: modular monolith by default; split into services only for a proven reason (independent scaling, team boundaries, fault isolation). Apply the fractal shape at each level. Rules and layout: `references/fractal-architecture.md`. Scaffold modules with `scripts/scaffold_module.py` so every module ships with a manifest.

### Phase 3: Database
Normalize first, denormalize on evidence. Derive indexes from the actual query list, not guesses. Migrations are backward compatible (expand/contract). Details and checklist: `references/db-schema-design.md`.

### Phase 4: API
Contract first (OpenAPI or schema), validation at the boundary, object-level authorization, cursor pagination, uniform errors, idempotency for unsafe retries. Details: `references/api-design.md`.

### Phase 5: Frontend UI/UX from scratch
Users and jobs, then information architecture, flows, tokens, components, states, accessibility, performance budgets. Generate a modular-scale token set with `scripts/design_tokens.py`. Details: `references/frontend-ux.md`. For distinctive visual direction beyond solid UX, use any design guidance the environment offers (a frontend-design skill, the project's existing design system).

### Phase 6: Implement in vertical slices, test first
Build the thinnest end-to-end slice first (UI to API to DB and back), with tests, then widen. Each slice: write the failing test from the requirement, implement in the Core, wire Adapters, register the module manifest, run the graph validator. This keeps accuracy checkable: every requirement traces to a test through the graph.

### Phase 7: Optimize with evidence
Profile before touching anything. Fix algorithmic and query problems by reasoning first (missing index, N+1, over-fetching). Use the GA tuner only for the remaining multi-parameter tuning where a benchmark exists. Procedure, fitness design, and the qualitative "design tournament" variant: `references/genetic-optimization.md`.

### Phase 8: Verify, document, make it evolvable
Run the quality gates in `references/quality-gates.md` (security checklist included). If a security review skill or scanner (SAST, dependency audit, secret scan) is available, run it on the generated code too. Run `scripts/kg_build.py validate`. Write ADRs for decisions that were non-obvious, store tuned genomes in the repo, and add fitness functions to CI (latency budget, bundle size, dependency rules) so the architecture defends itself.

## Scripts (stdlib-only Python 3, no installs)

Paths are relative to this skill's directory. Use `python3` (or `python` / `py -3` on Windows). If your environment cannot run commands, do the same work by hand: the reference files document every format and rule the scripts apply.

```bash
# Scaffold a fractal module with manifest, contract, core, adapters, tests
python scripts/scaffold_module.py orders --layer domain --root src/modules --ext ts

# Validate the knowledge graph against the ontology; analyze change impact
python scripts/kg_build.py validate --root src
python scripts/kg_build.py impact orders --root src       # affected nodes + tests to run
python scripts/kg_build.py mermaid --root src > docs/architecture/graph.mmd

# Genetic tuning of measurable parameters (see references/genetic-optimization.md)
python scripts/ga_tuner.py --config tuning/cache.json --out tuning/result.json
python scripts/ga_tuner.py --demo                          # self-test

# Design tokens (modular scale) and WCAG contrast check
python scripts/design_tokens.py --base 16 --ratio 1.25 > tokens.css
python scripts/design_tokens.py --contrast "#1a1a1a" "#ffffff"
```

The ontology lives in `assets/ontology.json` and the manifest template in `assets/module.template.json`. Copy the ontology into the project (`docs/architecture/ontology.json`) so the project owns it and can extend it.

## Working in any agent

This skill is written against capabilities, not product-specific tools, so it works in any coding agent:

| Capability | If missing |
|---|---|
| Read/write files | Output code blocks with full file paths and let the user place them |
| Run shell commands | Skip script runs, apply the rules by hand, and say what was not executed |
| Web access | Use the stack's stable core APIs, and flag versions as unverified |
| Sub-agents or parallelism | Not needed; run phases sequentially |
| Ask the user questions | State assumptions in one line and proceed |

Load only what the phase needs: this file first, then one reference file per phase, so small context windows stay usable. Never assume a tool name from one product; describe the action ("run the tests") and use whatever the host provides.

## Output contract

Match deliverables to task size, and say which you chose.

- **Greenfield app**: stack profile, requirement list, architecture sketch (modules and layers), schema (DDL or ORM models) with index rationale, OpenAPI or schema contract, UI plan (IA, flows, tokens, component inventory), then working code in slices with tests, graph validation output, and an ADR list.
- **Feature**: affected modules (from `impact`), schema migration (expand/contract), contract diff, UI states, tests, rollout notes.
- **Review or refactor**: findings ranked by risk with the gate each violates, smallest safe change first, tests that pin existing behavior before changing it.
- **Optimization**: baseline numbers, bottleneck evidence, change, after numbers, regression guard.

Keep prose short and put detail in files. Produce real, runnable code for the user's stack, not pseudocode, and say plainly what was not run or verified.

## Guardrails that matter

- **No cargo-cult cleverness.** If a plain approach meets the budgets, use it. A GA run that beats the baseline by less than measurement noise is not a result.
- **Security defaults are non-negotiable**: parameterized queries, output encoding, server-side authorization on every object access, secrets out of code, least-privilege credentials, dependency pinning, safe error messages. Details in `references/quality-gates.md`.
- **Never invent library APIs or versions.** If unsure, check docs (search if available) or write the code against the stable core API and flag the uncertainty.
- **Reversibility**: prefer changes that can be rolled back (feature flags, expand/contract migrations, additive API changes).
- **State assumptions** when the user's request is under-specified, then proceed instead of interrogating.
