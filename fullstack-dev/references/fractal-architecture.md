# Fractal Architecture

A fractal is self-similar: zoom in or out and the same shape appears. Apply that to code so a reader who understands one module understands them all, and so tooling (tests, budgets, graph checks) works identically at every scale.

## Contents
1. The repeating shape
2. Scales
3. Rules
4. Depth control (when to split or merge)
5. Fractal patterns beyond folders
6. Example layout
7. Anti-patterns

## 1. The repeating shape

Every unit, from the whole system down to a function, has four parts:

| Part | Meaning | At module scale | At system scale |
|---|---|---|---|
| **Contract** | What it promises; the only thing others may touch | public interface, types, events | OpenAPI / event schemas |
| **Core** | Pure logic, no I/O, deterministic | domain functions, rules | domain modules |
| **Adapters** | All I/O and framework glue, behind the contract's ports | repo impl, HTTP client, UI binding | gateways, DB, queues |
| **Proof** | Tests, budgets, manifest, observability | unit + contract tests, `module.json` | e2e, load tests, SLOs |

Why: the Core is trivially testable, Adapters are swappable (flexibility), the Contract is the stable seam (evolution), and the Proof makes each level independently verifiable.

## 2. Scales

1. **System**: frontend, backend, data stores, external services.
2. **Bounded context / service**: orders, billing, identity.
3. **Module**: a cohesive capability inside a context.
4. **Component / function**: smallest unit with its own contract (a React component with typed props, a service function with typed input/output).

Same questions at each scale: what is the contract, what is pure, what touches the world, how do we prove it?

## 3. Rules

1. **Dependency direction**: higher layers depend on lower ones only (`ui` > `api` > `domain` > `data` > `shared`). Dependencies point at Contracts, never at another module's internals. `kg_build.py validate` enforces this.
2. **One manifest per module** (`module.json`): id, layer, requirements implemented, depends_on, tests. This is the graph's source of truth.
3. **Budgets decompose**: a 300 ms p95 endpoint budget splits into child budgets (auth 20, domain 40, DB 120, serialization 20, slack 100). Each level asserts its own.
4. **Observability by node id**: logs, metrics, and traces carry the module id so production signals map back onto the graph.
5. **Errors cross boundaries as typed values or typed exceptions defined in the Contract**, never raw library errors.
6. **Configuration at the edge**: Core receives values, never reads env.

## 4. Depth control

Start shallow: **2 levels** (system, modules) for apps under roughly 10 KLOC or one team. Go deeper only on evidence.

Split a module when any holds: more than one reason to change; two sub-parts change at different rates; more than one team edits it; it exceeds about 400 cohesive lines with separable responsibilities; a sub-part needs independent scaling.

Merge when: a module has fan-in 1 and always changes with that one caller; it has no behavior of its own (pure pass-through).

Rule of three: extract shared code only after the third real use.

## 5. Fractal patterns beyond folders

- **Frontend**: atoms, molecules, organisms, pages, where each level is a component with typed props (Contract), pure view logic (Core), hooks/data fetching (Adapters), and a story + test (Proof). Feature folders mirror backend modules.
- **Data**: hierarchies (org > team > project) via recursive CTE, closure table, or `ltree`; tenancy applied identically at each level.
- **Caching**: the same cache-aside pattern at CDN, API, query, and memo levels, with invalidation keyed by entity ids from the graph.
- **UI spacing and type**: one ratio generating every size (see `frontend-ux.md`).
- **Testing**: the pyramid is fractal too; each scale gets the test type that matches its contract.

## 6. Example layout (stack-agnostic)

```
repo/
  docs/architecture/        ontology.json, graph.mmd, adr/
  src/
    shared/                 pure utilities, types, error base
    modules/
      orders/
        module.json
        contract/           types, ports, events, errors
        core/               pure domain logic
        adapters/           db repo, http handlers, queue publisher
        tests/              unit (core), contract, integration (adapters)
    web/                    frontend; features/orders mirrors modules/orders
  tuning/                   GA configs + tuned genomes (see genetic-optimization.md)
```

Map names to the stack's idioms (Django apps, Spring packages, Nest modules, Next.js route groups) rather than fighting the framework; keep the four-part shape.

## 7. Anti-patterns

- Empty ceremonial layers or one-class "modules".
- Contracts that leak ORM models or framework types.
- Shared "utils" that become a dumping ground (keep `shared` pure and small).
- Splitting into services before a modular monolith has shown a need.
- Cyclic dependencies hidden behind events with implicit ordering.
