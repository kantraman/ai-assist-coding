# Knowledge Graph and Ontology

The knowledge graph (KG) records *typed relationships* between the things in the system. The ontology defines which types and relationships are legal. Together they turn questions like "what breaks if I change X?" and "is every requirement tested?" into mechanical checks.

## Contents
1. Ontology
2. Module manifests
3. Workflow
4. Queries and what to do with them
5. Evolving the ontology
6. Using the graph elsewhere in this skill

## 1. Ontology (`assets/ontology.json`)

**Node types**: Requirement, Module, Entity, Table, Endpoint, Component, Test, Risk, Decision, ExternalService.

**Edge types** (with allowed from -> to):

| Edge | From | To | Meaning |
|---|---|---|---|
| `depends_on` | Module, Component | Module, Component, ExternalService | compile/runtime dependency (must be acyclic and layer-respecting) |
| `implements` | Module, Component, Endpoint | Requirement | satisfies a requirement |
| `exposes` | Module | Endpoint | publishes an API endpoint |
| `consumes` | Module, Component | Endpoint | calls an endpoint |
| `persists` | Module | Table | owns writes to a table |
| `models` | Table, Endpoint, Component | Entity | represents a domain entity |
| `tested_by` | Module, Component, Endpoint, Requirement | Test | verified by a test |
| `mitigates` | Module, Component, Decision | Risk | reduces a risk |
| `decided_by` | Module, Component, Table, Endpoint | Decision | rationale lives in an ADR |

**Layers** (rank): `ui` 4, `api` 3, `domain` 2, `data` 1, `shared` 0. A `depends_on` edge may not point to a higher rank.

**Rules** the validator enforces: known types, edge domain/range, no dangling or duplicate ids, `depends_on` acyclic, layer direction, every Requirement implemented, every Endpoint exposed, every Table persisted, every Module tested (warning).

## 2. Module manifests

Each module has a `module.json` beside its code (generate with `scripts/scaffold_module.py`; template: `assets/module.template.json`):

```json
{
  "id": "orders",
  "type": "Module",
  "layer": "domain",
  "nodes": [
    {"id": "Order", "type": "Entity"},
    {"id": "POST /orders", "type": "Endpoint"},
    {"id": "orders_table", "type": "Table"},
    {"id": "orders.unit", "type": "Test"}
  ],
  "edges": [
    {"rel": "implements", "to": "R1"},
    {"rel": "depends_on", "to": "pricing"},
    {"rel": "exposes", "to": "POST /orders"},
    {"rel": "persists", "to": "orders_table"},
    {"rel": "tested_by", "to": "orders.unit"},
    {"rel": "models", "from": "orders_table", "to": "Order"}
  ]
}
```

`from` defaults to the module's own id. Requirements are declared as nodes in a root manifest (for example `docs/module.json`) so they exist once and modules point at them.

## 3. Workflow

1. **Seed**: write requirements and entities into a root manifest.
2. **Grow with the code**: each time a module is created or its dependencies change, update its manifest in the same commit. Treat a stale manifest like a failing test.
3. **Validate** in CI: `python scripts/kg_build.py validate --root src` exits non-zero on errors (use `--strict` to fail on warnings too).
4. **Before changing code**: `python scripts/kg_build.py impact <id> --root src` lists affected nodes and the tests to run.
5. **Visualize**: `python scripts/kg_build.py mermaid --root src > docs/architecture/graph.mmd` for docs and reviews.

## 4. Queries and what to do with them

| Question | How | Action |
|---|---|---|
| What does a change to `pricing` affect? | `impact pricing` | run listed tests; review API consumers |
| Which requirements have no test? | validator warnings | write the test before the feature |
| Is anything violating layering? | validator errors | invert dependency via a contract port |
| Which modules are risky hubs? | `stats` (fan-in, fan-out, instability) | add contract tests, consider splitting |
| Is there dead code? | modules nothing depends on and nothing exposes | confirm and delete |

Instability `I = fan_out / (fan_in + fan_out)`: near 0 means stable (many depend on it, keep its contract steady and well tested); near 1 means volatile (free to change). Stable modules should be abstract (contracts); a stable module full of concrete churn is a smell.

## 5. Evolving the ontology

Version it (`"version"` field). Add a node or edge type only when a real question cannot be answered without it, and record the change as an ADR. Typical project-specific additions: `Job`, `Event`, `FeatureFlag`, `Permission`, with edges like `publishes`, `subscribes`, `guards`.

## 6. Using the graph elsewhere in this skill

- **Fractal architecture**: the manifest is the Proof part of each module; the validator enforces the dependency rule.
- **Genetic optimization**: pick genes from the hot path the graph shows (endpoints with the highest fan-in); use `impact` to know which tests to include in the fitness gates.
- **Testing**: derive the affected test set per change instead of running everything blindly, but keep a full run in CI.
- **Security**: tag modules that touch PII or credentials with a `Risk` node and require `mitigates` edges.
