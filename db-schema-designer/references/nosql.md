# NoSQL Schema Design Reference

Contents: Core mindset · Document (MongoDB/Firestore) · DynamoDB / key-value · Wide-column (Cassandra) · Redis · Consistency & integrity · Anti-patterns · Examples

## Core mindset

Relational design asks "what is the data?" and then queries it any way you like. NoSQL design asks "**how will it be queried?**" and shapes data to match. Therefore:

1. List access patterns first, with frequency and latency targets.
2. Design keys/partitions/embedding to serve each one with a single targeted read.
3. Accept duplication, because storage is cheap and cross-partition joins are not.
4. Decide where integrity is enforced (usually the application), and document it.
5. Adding a new access pattern later often means a new index, a new copy of the data, or a migration, so surface that cost to the user up front.

## Document stores (MongoDB, Firestore)

**Embed vs reference**

| Embed when | Reference when |
|---|---|
| Data is read together ("contains" relationship) | Child is large, unbounded, or grows over time |
| Child belongs to exactly one parent | Child is shared by many parents or queried alone |
| Child set is small and bounded | Child updated frequently and independently |
| Atomic single-document update is wanted | Document would approach the size limit (MongoDB 16 MB, Firestore 1 MiB) |

**Patterns**
- **Subset pattern**: embed only the most recent or top-N children (e.g. last 10 reviews) and keep the full set in a separate collection.
- **Extended reference**: copy a few frequently displayed fields from the referenced doc (`author: {id, name, avatar}`) to avoid lookups. Plan how updates propagate.
- **Bucket pattern**: group time-series points into per-hour/day bucket documents to cut document and index counts (MongoDB also offers native time-series collections).
- **Computed pattern**: store precomputed aggregates/counters, updated on write.
- **Polymorphic pattern**: one collection with a `type` field for similar entities with differing fields.
- **Schema versioning**: include `schemaVersion` so old and new shapes can coexist during migration.
- **Outlier pattern**: handle rare giant documents (a celebrity with millions of followers) by overflow documents.

**Indexing (MongoDB)**
- Follow **ESR**: Equality, Sort, Range for compound index field order.
- Use partial, sparse, TTL (expiring data), and multikey (array) indexes where fitting. Avoid indexing large unbounded arrays.
- Use schema validation (`$jsonSchema`) to get some structure enforcement.
- Choose shard keys with high cardinality, even distribution, and query isolation. Avoid monotonically increasing keys (use hashed sharding if necessary).

**Firestore specifics**: queries must be served by indexes (single-field automatic, composite manual). Avoid hot documents (about 1 write/sec/document sustained). Model with subcollections for unbounded children.

## DynamoDB / key-value

**Start from access patterns**, then define keys. Prefer **single-table design** when patterns are known and stable and joins are needed. Use multiple tables for independent entities, unclear/changing patterns, or team clarity.

**Key design**
- **Partition key (PK)**: high cardinality, uniform traffic. Avoid hot keys (low cardinality such as `status`, or a single date). Mitigate with write sharding (`PK#<n>` suffix) when needed.
- **Sort key (SK)**: enables range queries (`begins_with`, `between`) and models hierarchies and 1:N within a partition (`ORDER#2026-05-01#123`).
- Generic attribute names (`PK`, `SK`, `GSI1PK`, `GSI1SK`) and prefixed values (`USER#42`, `ORDER#99`) make single-table designs readable. Always document the key schema in a table.
- **GSIs** support alternate access patterns (eventually consistent, own throughput). **Sparse GSIs** (only items with the attribute are indexed) are an efficient way to index a subset. LSIs must be created at table creation and cap partition size at 10 GB, so use them rarely.
- Items max 400 KB; large payloads go to S3 with a pointer.
- Use `Query`, not `Scan`, on hot paths. Use TTL for expiry. Use conditional writes for uniqueness and optimistic locking. Use `TransactWriteItems` (limited to 100 items) for multi-item atomicity.
- Pagination via `LastEvaluatedKey`.

**Mapping table (always include in output)**

| Access pattern | Index | Key condition |
|---|---|---|
| AP1 Get user | Table | PK = `USER#id`, SK = `PROFILE` |
| AP2 User's orders, newest first | Table | PK = `USER#id`, SK begins_with `ORDER#`, ScanIndexForward=false |
| AP3 Order by id | GSI1 | GSI1PK = `ORDER#id` |

## Wide-column (Cassandra, ScyllaDB)

- **One table per query.** Denormalize freely and write to several tables.
- Primary key = `((partition key columns), clustering columns)`. The partition key decides distribution, clustering columns decide on-disk order within a partition and thus range queries.
- Target partitions of roughly <100 MB and <100k rows. Bound growth by adding a time bucket to the partition key (`(sensor_id, day)`).
- Queries must supply the full partition key. No joins, limited ad hoc filtering, and avoid `ALLOW FILTERING`.
- Avoid secondary indexes on high-cardinality columns and heavy use of materialized views. Prefer explicit query tables.
- Model deletes carefully: tombstones hurt, so prefer TTL and time-bucketed partitions that expire whole.
- Choose clustering order to match the most common read (`CLUSTERING ORDER BY (ts DESC)`).

## Redis

- Choose the data structure to match the use: String (cache, counters), Hash (objects), List (queues), Set (membership, tags), Sorted Set (leaderboards, time-ordered indexes), Stream (event logs), Bitmap/HyperLogLog (flags, approximate uniques).
- **Key naming**: `app:entity:id[:field]`, e.g. `shop:user:42:cart`. Keep it consistent and documented.
- Always set TTLs for cache and session data. Avoid huge keys/collections (large sorted sets and hashes block the single thread on big operations).
- Redis is rarely the system of record. State the durability model (RDB/AOF) and the rebuild path if used for primary data.
- Use secondary-index-style sets or sorted sets, maintained by the app, if lookup by non-key is needed. Consider RediSearch/JSON for richer querying.

## Consistency and integrity

NoSQL stores generally lack foreign keys and cross-entity constraints. For each invariant, say **where it is enforced**:
- Uniqueness: unique index (Mongo), conditional write on a dedicated lookup item (DynamoDB), lightweight transactions (Cassandra, use sparingly).
- Referential integrity: application logic, cleanup jobs, or tolerance of dangling references.
- Multi-entity atomicity: transactions where supported (Mongo multi-document, DynamoDB transactions) but design so most operations touch one document/partition.
- Duplicated data: define the propagation strategy (synchronous multi-write, change streams / DynamoDB Streams / CDC, or periodic reconciliation) and the acceptable staleness.

## Anti-patterns

- Normalizing into many collections and joining in the application (`$lookup` on hot paths)
- Unbounded arrays or ever-growing documents
- Hot partitions: sequential IDs/timestamps or low-cardinality values as partition key
- `Scan`/collection scans or `ALLOW FILTERING` for production queries
- One giant "everything" document that is rewritten for every small update
- Designing before knowing the access patterns
- Choosing NoSQL when requirements need ad hoc querying, heavy reporting, or strong multi-entity transactions

## Examples

### MongoDB: blog (embed bounded, reference unbounded)

```js
// posts
{
  _id: ObjectId,
  slug: "intro-to-indexes",            // unique index
  title: "Intro to Indexes",
  author: { _id: ObjectId, name: "Ada" },   // extended reference
  tags: ["db", "performance"],               // bounded array, multikey index
  body: "...",
  stats: { views: 1042, commentCount: 17 },  // computed pattern
  recentComments: [ /* last 5 only */ ],     // subset pattern
  publishedAt: ISODate,
  schemaVersion: 2
}
// comments (unbounded -> separate collection)
{ _id, postId, author: {_id, name}, text, createdAt }
// Indexes
// posts:    { slug: 1 } unique; { tags: 1, publishedAt: -1 }; { "author._id": 1, publishedAt: -1 }
// comments: { postId: 1, createdAt: -1 }
```

### DynamoDB: single-table orders

| Entity | PK | SK | GSI1PK | GSI1SK |
|---|---|---|---|---|
| Customer | `CUST#42` | `PROFILE` | `EMAIL#a@x.com` | `CUST` |
| Order | `CUST#42` | `ORDER#2026-05-01T10:00Z#o99` | `ORDER#o99` | `ORDER` |
| Order item | `ORDER#o99` | `ITEM#001` | | |

Serves: get customer (PK+SK), customer's orders newest-first (PK, SK begins_with `ORDER#`, descending), customer by email (GSI1), order by id (GSI1), items of an order (Query PK=`ORDER#o99`).

### Cassandra: sensor readings

```sql
CREATE TABLE readings_by_sensor_day (
  sensor_id text,
  day       date,
  ts        timestamp,
  value     double,
  PRIMARY KEY ((sensor_id, day), ts)
) WITH CLUSTERING ORDER BY (ts DESC)
  AND default_time_to_live = 7776000;  -- 90 days
```
