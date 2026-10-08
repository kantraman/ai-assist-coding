# Performance Reference

Read this when the user asks for optimization, or when reviewing code that handles large inputs, loops over data, or touches I/O. Contents: principles, free habits, optimization ladder, common patterns, caching, concurrency, language notes, how to measure.

## Principles

1. **Measure first.** Intuition about bottlenecks is frequently wrong.
2. **Complexity beats constants.** Going from O(n²) to O(n) outclasses any micro-optimization.
3. **I/O dominates.** Network, disk, and database calls cost orders of magnitude more than CPU work. Reduce their count before tuning their code.
4. **Optimize the hot path only.** If a function runs once at startup, leave it readable.
5. **Keep a correctness safety net.** Tests must pass before and after.

## Free habits (apply by default)

- Use hash-based structures (set, dict/map) for membership and lookup instead of scanning lists.
- Hoist invariants out of loops (compiled regexes, constants, repeated lookups, config reads).
- Build strings with join/builders, not repeated concatenation in loops.
- Use generators/iterators/streams when you don't need the whole collection in memory.
- Fetch only needed columns/rows; push filtering and aggregation to the database.
- Batch operations (bulk inserts, batched API calls) instead of one-at-a-time in a loop.
- Exit early when the answer is known (short-circuit, `any`/`all`, break).

## Optimization ladder (work top to bottom)

1. **Algorithm and data structure**: sorting vs. repeated scans, hashing vs. nested loops, heaps for top-k, binary search on sorted data, precomputation, two-pointer/sliding window.
2. **I/O reduction**: fix N+1 queries, add missing database indexes (check the query plan), batch and paginate, compress payloads, avoid redundant reads.
3. **Caching and memoization**: see below.
4. **Concurrency/parallelism**: for I/O-bound work use async or threads; for CPU-bound work use processes or native extensions (respect the language's constraints, e.g. Python's GIL).
5. **Memory and allocation**: reuse buffers, avoid needless copies, choose compact representations, pool expensive objects.
6. **Language/runtime-level tuning**: vectorization (NumPy, SIMD), compiled hot paths, JIT-friendly code. Last resort, and measure.

## Common patterns

**N+1 queries**
Symptom: a query inside a loop over query results. Fix: join, `IN (...)` batch, or eager-loading/prefetch.

**Quadratic membership checks**
Symptom: `if x in some_list` inside a loop. Fix: build a set once before the loop.

**Repeated parsing/compilation**
Symptom: regex, JSON schema, or template compiled each call. Fix: compile once at module/initialization scope.

**Materializing everything**
Symptom: reading a whole file/result set into memory to iterate once. Fix: stream line-by-line or chunk by chunk.

**Chatty services**
Symptom: many small sequential network calls. Fix: batch endpoints, parallel requests with bounded concurrency, caching of stable data.

**Sorting to find min/max/top-k**
Symptom: sort the full list to take a few elements. Fix: `min`/`max`, heap (`nlargest`), or selection.

## Caching guidance

Cache when computation or fetch is expensive, results are reused, and staleness is tolerable. Always decide:
- **Key**: what uniquely determines the result?
- **Invalidation**: TTL, explicit invalidation on write, or immutability of inputs?
- **Size bound**: unbounded caches are memory leaks (use LRU or max size).
- **Concurrency**: avoid thundering herds (single-flight / locking on miss).
- **Correctness**: never cache per-user data under a shared key.

Document these decisions in a short comment; caches are a common source of subtle bugs.

## Concurrency guidance

- Prefer the simplest model that works: sequential, then async/threads for I/O, then processes for CPU.
- Bound concurrency (semaphores, worker pools) so you don't overwhelm downstream services.
- Avoid shared mutable state; pass messages or use immutable data.
- Set timeouts on every external call. Handle partial failure and cancellation.

## Language notes (adapt to the project's language)

- **Python**: prefer comprehensions/generators, built-ins (`sum`, `any`, `sorted`), `collections` (`defaultdict`, `Counter`, `deque`), `functools.lru_cache`; vectorize numeric loops with NumPy/pandas; avoid per-row Python loops over DataFrames.
- **JavaScript/TypeScript**: avoid blocking the event loop; use `Promise.all` for independent async calls (bounded); avoid repeated array copies in loops; use `Map`/`Set` for lookups.
- **Java/C#/Go/Rust**: watch allocations in hot loops, use buffered I/O, size collections up front when known, prefer streaming APIs; in Go, mind goroutine leaks and channel blocking.
- **SQL**: index columns used in filters/joins/ordering, avoid `SELECT *`, avoid functions on indexed columns in `WHERE`, inspect `EXPLAIN` output.

## How to measure

- Use the language's profiler to find where time actually goes (cProfile/py-spy, Chrome DevTools/clinic.js, pprof, JFR, etc.).
- Benchmark with realistic data sizes; warm up; repeat; compare medians, not single runs.
- Check both time and memory.
- Report before/after numbers with the input size and environment. If you can't run code, state the expected complexity change and label it as an estimate.
