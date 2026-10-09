---
name: db-schema-designer
description: Design database schemas for SQL (PostgreSQL, MySQL, SQL Server, SQLite) and NoSQL (MongoDB, DynamoDB, Cassandra, Redis, Firestore) with a focus on query performance, data integrity, and clarity. Use this skill whenever the user wants to design, model, review, normalize, denormalize, or optimize a database schema, data model, ER diagram, table structure, collection structure, indexes, partition keys, or migrations, even if they only say "how should I store this data", "what tables do I need", "help me model X", or "should I use SQL or NoSQL". Also use it to critique an existing schema, choose between relational and document/key-value/wide-column stores, or turn app requirements into DDL or collection/table designs.
---

# DB Schema Designer

Produce schemas that are correct first, fast second, and easy to read third. A good design starts from how the data is **used**, not just what it **is**: the access patterns decide indexes, denormalization, and (for NoSQL) the entire shape of the data.

## Workflow

### 1. Gather requirements (briefly)

Extract from the conversation what you can. Ask at most a few targeted questions for what's missing and material to the design. If the user wants you to proceed, state your assumptions and go on.

Needed information:
- **Entities and relationships**: what are the things, and how do they relate (1:1, 1:N, M:N)?
- **Access patterns**: the top reads and writes, with rough frequency. ("Show a user's last 20 orders", "look up by email", "dashboard aggregates by day".)
- **Scale and shape**: expected row/document counts, growth, read/write ratio, hot spots.
- **Consistency needs**: are multi-entity transactions required (payments, inventory)? Is eventual consistency acceptable?
- **Engine constraints**: existing stack, cloud provider, team expertise.

### 2. Choose the engine

If the user has already chosen, use it. Otherwise recommend with reasons using this guide:

| Situation | Lean toward |
|---|---|
| Many relationships, ad hoc queries, strong integrity, transactions | Relational (PostgreSQL default) |
| Aggregates read/written as a unit, flexible or nested attributes | Document (MongoDB, Firestore) |
| Known, key-based access at massive scale, predictable latency | DynamoDB / key-value |
| Huge write throughput, time-series, queries always by partition | Wide-column (Cassandra, ScyllaDB) |
| Caching, sessions, counters, leaderboards, queues | Redis |
| Mixed needs | Relational core plus a specialized store for the hot path (polyglot) |

Default to relational unless access patterns clearly justify otherwise. Say so plainly: it keeps the user from choosing NoSQL for fashion.

### 3. Read the matching reference

- Relational design: read `references/sql.md`
- Document, key-value, wide-column, Redis: read `references/nosql.md`
- Comparing both or polyglot: read both

### 4. Design

Work in this order:
1. Entities and relationships (conceptual model)
2. Schema (tables/collections, keys, types, constraints)
3. Indexes / partition and sort keys mapped to each access pattern
4. Deliberate denormalization or embedding, each justified by a pattern
5. Growth and evolution plan (partitioning, archiving, migrations)

### 5. Validate against access patterns

Walk every access pattern through the design and confirm it is served by an index or key, without full scans, N+1 loops, or cross-partition fan-out. Fix gaps before presenting. This step is what separates a schema that looks tidy from one that performs.

## Output format

Use this structure for a full design. Scale it down for small questions; a one-table question needs a short answer, not seven sections.

```
# <System> Schema Design

## Summary
2-4 sentences: engine choice, core modeling approach, key trade-off.

## Assumptions & access patterns
Numbered list. These are referenced later (AP1, AP2, ...).

## Entity relationship overview
Mermaid erDiagram (SQL) or a structure/relationship diagram (NoSQL).

## Schema
Runnable DDL (SQL) or collection/table definitions with sample documents/items (NoSQL).

## Indexes / keys
Table mapping each access pattern to the index or key that serves it.

## Design decisions & trade-offs
Why this normalization level, why this embedding, what was rejected and why.

## Scaling & evolution
Partitioning, archiving, hot-key risks, migration approach.
```

Deliver DDL longer than ~20 lines as a file (`schema.sql`, or `schema.md` for NoSQL), and present it with `present_files`. Short snippets can stay inline.

## Cross-cutting principles

- **Name things consistently.** Pick a convention (snake_case plural tables, singular `id`, `<entity>_id` foreign keys) and apply it everywhere. Clarity is a feature, because schemas outlive their authors.
- **Model the domain truthfully.** Use the right type (`timestamptz`, `numeric(12,2)` for money, never float), enums or lookup tables for closed sets, and `NOT NULL` by default.
- **Let the database enforce rules.** Constraints, foreign keys, and unique indexes beat application-only validation. Where an engine can't enforce them (most NoSQL), say where the invariant lives.
- **Index for queries, not hope.** Every index costs write speed and storage. Justify each by an access pattern, and drop ones that nothing uses.
- **Denormalize on purpose.** Duplicating data is fine when it removes a hot-path join or fan-out, but record what must be kept in sync and how.
- **Plan for change.** Prefer additive migrations, avoid designs that need rewriting every row to evolve, and include `created_at`/`updated_at` unless there's a reason not to.
- **Be explicit about security and privacy.** Flag PII columns, suggest encryption or separation for sensitive fields, and think about retention and soft vs hard deletes.

## Reviewing an existing schema

When the user provides a schema to critique:
1. Restate what you think it models and which access patterns it appears to serve. Confirm if unclear.
2. List findings by severity: **Correctness/integrity** (missing keys, wrong types, anomalies), **Performance** (missing/redundant indexes, scans, hot partitions), **Clarity** (naming, structure).
3. For each finding give the problem, why it matters, and a concrete fix (DDL or migration steps).
4. Provide a safe migration order if changes touch live data (add, backfill, switch, then drop).

## Common mistakes to catch

- Storing lists in a delimited string or JSON column when a child table is needed (SQL)
- Entity-Attribute-Value tables used to dodge modeling
- Missing indexes on foreign keys; duplicate or left-prefix-redundant indexes
- `SELECT *` hot paths with wide rows, and unbounded `OFFSET` pagination
- Unbounded arrays inside documents; documents growing without limit (NoSQL)
- Low-cardinality or monotonically increasing partition keys causing hot partitions
- Modeling NoSQL like relational (many collections plus app-side joins)
- Using NoSQL where multi-entity transactions are central
