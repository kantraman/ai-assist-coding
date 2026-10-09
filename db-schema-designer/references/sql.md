# Relational (SQL) Schema Design Reference

Contents: Modeling steps · Normalization · Keys & types · Constraints · Indexing · Relationships · Performance patterns · Engine notes · Example

## Modeling steps

1. Identify entities (nouns) and attributes.
2. Define relationships and cardinality; resolve M:N with a junction table.
3. Normalize to 3NF as the baseline.
4. Add keys, types, and constraints.
5. Add indexes per access pattern.
6. Denormalize selectively, only with measured or clearly predicted need.

## Normalization

- **1NF**: atomic values, no repeating groups (no `tag1, tag2, tag3` columns or comma-separated lists).
- **2NF**: every non-key attribute depends on the whole key (matters for composite keys).
- **3NF**: no transitive dependencies (e.g. don't store `city` and `zip_code -> city` in the same table).
- Stop at 3NF/BCNF for OLTP. Go further only for specific anomalies.

**When to denormalize** (always document the sync mechanism):
- Read-heavy hot path where a join over large tables dominates latency
- Precomputed aggregates (`order_total`, `comment_count`) maintained by trigger, app code, or materialized view
- Historical snapshots that must not change when the source changes (e.g. `unit_price` copied onto `order_items`, shipping address copied onto an order)
- Reporting: prefer a separate star-schema/warehouse or materialized views over polluting the OLTP model

## Keys and types

**Primary keys**
- Default: surrogate key. PostgreSQL: `bigint GENERATED ALWAYS AS IDENTITY`, MySQL: `BIGINT AUTO_INCREMENT`.
- UUIDs when IDs are generated across services or must not be guessable. Prefer time-ordered UUIDs (UUIDv7 / ULID) over random v4 for large tables, since random keys fragment B-tree indexes (especially clustered ones such as InnoDB).
- Keep natural keys (email, SKU) as `UNIQUE` constraints, not primary keys, because they change.
- Junction tables: composite PK of the two FKs is fine.

**Types**
- Money: `numeric(p,s)` or integer minor units (cents) plus a currency code. Never `float`.
- Time: `timestamptz` (PostgreSQL), store UTC. Use `date` when time is irrelevant.
- Text: `text` (PostgreSQL) or an appropriately sized `VARCHAR` elsewhere. Add a `CHECK` for length if it matters.
- Booleans: real `boolean`. Closed value sets: enum type, `CHECK`, or a lookup table (use a lookup table if values carry attributes or change often).
- JSON/JSONB: for genuinely sparse or schemaless attributes. Not a substitute for modeling queryable, relational data. Index with GIN or expression indexes when queried.
- Use the smallest integer type that safely fits. Row width affects cache efficiency.

## Constraints

Prefer enforcement in the database:
- `NOT NULL` by default; allow null only when "unknown/not applicable" is meaningful.
- `FOREIGN KEY` with an explicit `ON DELETE` choice: `RESTRICT` (default safe), `CASCADE` (true ownership, e.g. order -> order_items), `SET NULL` (optional references).
- `UNIQUE` (including partial/filtered unique indexes, e.g. unique email where `deleted_at IS NULL`).
- `CHECK` for domain rules (`quantity > 0`, `end_at > start_at`).
- Soft delete (`deleted_at`) complicates uniqueness and every query. Use it only when recovery or audit requires it, and consider an archive table instead.

## Indexing

- Index every foreign key used in joins or cascades (PostgreSQL doesn't do this automatically).
- **Composite index order**: equality columns first, then range/sort columns. Left-prefix rule: `(a, b, c)` serves `a`, `a,b`, `a,b,c`, not `b` alone.
- A composite index makes a single-column index on its leading column redundant.
- **Covering indexes** (`INCLUDE` in PostgreSQL/SQL Server) avoid table lookups for hot queries.
- **Partial indexes** for skewed data: `WHERE status = 'pending'`.
- **Expression indexes** for `lower(email)` and similar.
- Match index type to the job: B-tree (default), GIN (JSONB, arrays, full-text), GiST (geo, ranges), BRIN (huge append-only, naturally ordered tables).
- Don't index low-cardinality booleans alone. Don't over-index write-heavy tables.
- Verify with `EXPLAIN (ANALYZE, BUFFERS)` on realistic data volumes, and mention that the user should do so.

## Relationships

- **1:N**: FK on the "many" side.
- **M:N**: junction table with its own attributes (e.g. `enrolled_at`, `role`), composite PK or surrogate PK plus a unique constraint, and indexes in both directions if both are queried.
- **1:1**: share the PK (`user_profiles.user_id` is both PK and FK), or split only for wide/rare/sensitive columns.
- **Hierarchies**: adjacency list (`parent_id`) plus recursive CTEs is the simple default. Use `ltree`/materialized path for read-heavy trees, closure table for frequent ancestor/descendant queries.
- **Polymorphic references**: avoid `(entity_type, entity_id)` without FKs. Prefer separate nullable FKs with a `CHECK` that exactly one is set, or a shared supertype table.
- **Multi-tenancy**: `tenant_id` on every table, leading column in composite indexes and in composite FKs. Consider PostgreSQL row-level security. Schema-per-tenant or DB-per-tenant only when isolation needs justify it.

## Performance patterns

- **Pagination**: keyset/seek (`WHERE (created_at, id) < (:c, :i) ORDER BY created_at DESC, id DESC LIMIT n`) over `OFFSET` for deep pages.
- **Counters**: avoid `COUNT(*)` on huge tables in hot paths. Keep a maintained counter or approximate count.
- **Partitioning**: range-partition large time-series/log tables (by month, for example) so old data can be dropped by detaching partitions. The partition key must be in the PK/unique constraints.
- **Archiving**: move cold rows to an archive table or storage.
- **Wide rows**: move rarely read large blobs/text into a side table or object storage and keep a reference.
- **Audit/history**: separate `_history` table or temporal tables rather than overloading the main table.
- **Idempotency**: unique constraint on an idempotency key for payment/webhook-style writes.
- **Concurrency**: optimistic locking with a `version` column, `SELECT ... FOR UPDATE SKIP LOCKED` for queues, and constraints rather than check-then-insert races.

## Engine notes

- **PostgreSQL**: richest feature set (JSONB, partial/expression/GIN/GiST/BRIN indexes, RLS, CTEs, generated columns). Default recommendation.
- **MySQL/InnoDB**: PK is the clustered index, so keep it small and ordered, because every secondary index carries the PK. Limited partial/expression index support (functional indexes since 8.0).
- **SQL Server**: clustered vs nonclustered, filtered indexes, `INCLUDE` columns, columnstore for analytics.
- **SQLite**: type affinity is loose, so use `STRICT` tables where available, and enable `PRAGMA foreign_keys = ON`. Suited to embedded/single-writer workloads.

## Example (PostgreSQL, e-commerce core)

```sql
CREATE TABLE customers (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email       text NOT NULL,
    full_name   text NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX customers_email_uq ON customers (lower(email));

CREATE TABLE products (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku          text NOT NULL UNIQUE,
    name         text NOT NULL,
    price_cents  integer NOT NULL CHECK (price_cents >= 0),
    currency     char(3) NOT NULL DEFAULT 'USD',
    attributes   jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TYPE order_status AS ENUM ('pending','paid','shipped','cancelled');

CREATE TABLE orders (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id   bigint NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    status        order_status NOT NULL DEFAULT 'pending',
    total_cents   integer NOT NULL CHECK (total_cents >= 0),  -- denormalized; set at checkout
    placed_at     timestamptz NOT NULL DEFAULT now()
);
-- AP: "customer's recent orders" (equality + sort)
CREATE INDEX orders_customer_placed_idx ON orders (customer_id, placed_at DESC);
-- AP: "work queue of pending orders" (partial)
CREATE INDEX orders_pending_idx ON orders (placed_at) WHERE status = 'pending';

CREATE TABLE order_items (
    order_id          bigint NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    line_no           smallint NOT NULL,
    product_id        bigint NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity          integer NOT NULL CHECK (quantity > 0),
    unit_price_cents  integer NOT NULL CHECK (unit_price_cents >= 0),  -- snapshot at purchase
    PRIMARY KEY (order_id, line_no)
);
CREATE INDEX order_items_product_idx ON order_items (product_id);  -- FK index
```
