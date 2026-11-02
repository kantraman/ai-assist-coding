# Performance Checklist

Optimize what matters at the expected scale; correctness and clarity come first. State assumptions about scale in the intent contract.

## Algorithmic
- Identify the hot path and state its time/space complexity. Flag anything quadratic or worse on data that can grow.
- Use the right structure: sets/dicts for membership and lookup, heaps for top-k, deques for queues, sorted/indexed structures for range queries.
- Avoid repeated work: hoist invariants out of loops, memoize pure expensive calls, don't re-parse or re-compile (compile regexes once).

## I/O and data access
- **N+1**: no query/HTTP call per item in a loop; batch (`IN` queries, joins, bulk APIs, dataloaders).
- Select only needed columns; paginate; stream large files/results instead of loading into memory.
- Indexes exist for every frequent filter/join/sort; verify with `EXPLAIN` when SQL is non-trivial.
- Reuse connections (pools, keep-alive sessions); set timeouts.
- Prefer bulk inserts/upserts over row-by-row writes; wrap in a transaction.

## Memory
- No unbounded collections or caches; set max sizes/TTL. Beware accumulating state in long-lived processes.
- Generators/iterators for pipelines; avoid building large intermediate lists.
- Watch string concatenation in loops; use join/builders.

## Concurrency
- Use async or worker pools for I/O-bound work; processes or native code for CPU-bound work.
- Bound concurrency (semaphores, pool size) so load can't exhaust sockets, memory, or downstream services.
- Don't block the event loop; no sync I/O in async code.
- Locks are short and fine-grained; avoid holding them across I/O.

## Caching
- Cache only where the cost is real; define key, TTL, invalidation, and stampede behavior. Never cache per-user data under a shared key.

## Measure
- Where practical, include a small benchmark or timing check with a realistic input size, and report the numbers. Claim speed-ups only with measurements or clear complexity arguments.
