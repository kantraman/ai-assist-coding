# Database Schema Design

## Contents
1. Process
2. Modeling rules
3. Keys and types
4. Indexing
5. Migrations
6. Multi-tenancy, history, hierarchy
7. Scaling ladder
8. Choosing the store
9. Schema doc template

## 1. Process

1. List entities and relationships from the requirements (graph: Entity nodes).
2. List the **queries and writes** the app performs, with expected frequency and latency. Indexes come from this list.
3. Normalize to 3NF. Denormalize only where a measured query needs it, and document the invariant that keeps copies consistent.
4. Add constraints in the database, not only in app code: `NOT NULL`, `UNIQUE`, `CHECK`, foreign keys.
5. Write DDL or ORM models, then **verify with `EXPLAIN (ANALYZE)`** on realistic data volumes.
6. Add the migration, a rollback plan, and seed/fixture data for tests.

## 2. Modeling rules

- One fact in one place. Join tables for many-to-many, with a composite unique key.
- Use `CHECK` constraints and enums/lookup tables for closed value sets; prefer lookup tables if values change at runtime.
- JSONB/JSON only for genuinely schemaless or sparse attributes; never for data you filter, join, or constrain heavily.
- Soft delete (`deleted_at`) only if undo or audit requires it; then every query and unique index must account for it (partial unique index `WHERE deleted_at IS NULL`).
- Store derived values only with a documented refresh path (trigger, job, or materialized view).

## 3. Keys and types

- Primary keys: `bigint` identity for internal tables, or time-ordered UUID (v7) when ids are generated client-side or exposed. Avoid random UUIDv4 as clustered key on large write-heavy tables.
- Money: integer minor units or `numeric(p,s)`, plus currency code. Never floating point.
- Time: `timestamptz` in UTC; store the user's zone separately if needed. Add `created_at`, `updated_at`.
- Text: set sensible length limits via `CHECK`; use case-insensitive unique indexes for emails (`lower(email)` or `citext`).
- Booleans that grow into states should be a status column from the start.

## 4. Indexing

- Index foreign keys and every column used in frequent `WHERE`, `JOIN`, `ORDER BY`.
- Composite index order: equality columns first, then range, then sort. Leading column must match the filter.
- Partial indexes for hot subsets (`WHERE status = 'open'`); covering indexes (`INCLUDE`) to avoid heap fetches on hot reads.
- Every index slows writes and uses memory: justify each one with a query. This is a natural GA gene set (index on/off) once a benchmark exists; see `genetic-optimization.md`.
- Pagination: keyset (`WHERE (created_at, id) < (:c, :i) ORDER BY created_at DESC, id DESC`) over `OFFSET`.
- Watch for N+1 in the ORM layer; fix with joins, batching, or dataloaders.

## 5. Migrations

- Tool per stack (Flyway/Liquibase, Alembic, Prisma Migrate, Django/Rails/Laravel migrations, Atlas, goose).
- **Expand, migrate, contract**: add nullable column or new table; dual-write/backfill in batches; switch reads; remove old structure in a later release. Never rename or drop in the same deploy that stops using it.
- Adding a `NOT NULL` column: add nullable, backfill, then add the constraint (use `NOT VALID` then `VALIDATE` where supported).
- Create indexes concurrently on large live tables.
- Every migration is tested against a copy of realistic data and is idempotent or safely re-runnable in CI.

## 6. Tenancy, history, hierarchy

- **Multi-tenant**: `tenant_id` on every tenant-owned table, part of composite keys and indexes; enforce with row-level security where available, plus tests that prove cross-tenant reads fail.
- **Audit/history**: append-only audit table or temporal table; capture actor, action, before/after.
- **Hierarchies**: adjacency list + recursive CTE for shallow trees; closure table or `ltree` for deep/frequent subtree queries.
- **Reliable events**: transactional outbox table written in the same transaction as the state change, relayed by a worker; consumers are idempotent.
- **Idempotency**: unique constraint on (client_id, idempotency_key) for retried writes.

## 7. Scaling ladder (climb only when measurements demand it)

1. Right indexes and query shapes. 2. Connection pooling. 3. Caching (app/Redis/CDN). 4. Read replicas (mind lag). 5. Partitioning for time-series or huge tables. 6. Archival of cold data. 7. Sharding or a specialized store (last resort).

## 8. Choosing the store

Default to PostgreSQL (or the user's stack default such as MySQL/MariaDB, SQL Server) for relational OLTP. Add Redis for caching/queues/rate limits, search engines for full-text relevance, object storage for blobs, columnar/OLAP stores for analytics. Document why each extra store exists.

## 9. Schema doc template

```
Entity: Order   (R1, R4)
Table: orders   owner module: orders
Columns: id bigint PK, customer_id FK->customers, status text CHECK in (...), total_cents bigint >= 0, created_at timestamptz
Constraints: ...
Indexes: (customer_id, created_at DESC) for "my orders"; partial (status) WHERE status='open' for worker
Queries served: Q1 list my orders (p95 < 50ms), Q2 claim open orders (batch 100)
Data volume: 5M rows/yr; retention 7 yr; PII: none
Migration notes: expand/contract steps
```
