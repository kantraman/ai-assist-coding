---
name: code-quality
description: Guidelines for writing and revising code that is both efficient and easy to maintain. Use this skill whenever generating, refactoring, reviewing, or optimizing code in any language, including requests like "make this faster", "clean this up", "refactor", "improve performance", "reduce complexity", "make this maintainable", or "review my code". Also use it when writing any non-trivial new code (functions, modules, scripts, services), even if the user never mentions quality, because maintainability and sensible performance should be the default.
---

# Code Quality: Optimization and Maintainability

Code is read and changed far more often than it is written, and most code is not performance-critical. So the priorities, in order, are:

1. **Correct**: it does what was asked, including edge cases.
2. **Clear**: the next reader (human or agent) can understand and change it safely.
3. **Fast enough**: no avoidable inefficiency, with deeper optimization only where evidence justifies it.

Clarity comes before speed because unclear code that is fast today becomes buggy and slow tomorrow, once nobody dares touch it. The exception is code with a known hot path or an explicit performance requirement.

## Workflow

### 1. Understand before changing
- Read the surrounding code, conventions, and tests first. Match the existing style, naming, error handling, and project structure rather than imposing your own.
- Identify the intent. If the request is ambiguous (e.g. "optimize this" with no target), state your assumption about what matters (latency, memory, readability, throughput) and proceed.
- For modifications, keep the diff focused. Don't rewrite unrelated code; mention it instead.

### 2. Write for the reader
Apply the rules in `references/maintainability.md`. The essentials:
- Names describe intent (`retry_count`, not `n`). A good name removes the need for a comment.
- Functions do one thing, at one level of abstraction. If you need "and" to describe it, split it.
- Prefer flat control flow: guard clauses and early returns over deep nesting.
- No magic numbers or strings; name them as constants.
- Comments explain *why* (constraints, trade-offs, non-obvious decisions), never restate *what* the code does.
- Handle errors deliberately: fail loudly with useful context; never swallow exceptions silently.
- Avoid duplication once it appears a third time, but don't abstract prematurely. A wrong abstraction costs more than a little repetition.
- Keep dependencies and side effects at the edges; keep core logic pure and easy to test.

### 3. Choose sensible performance by default
Without profiling, do the things that are free in readability terms (see `references/performance.md`):
- Pick the right data structure (set/dict lookups instead of repeated list scans).
- Avoid accidental quadratic work: nested loops over large inputs, repeated string concatenation in loops, queries inside loops (N+1).
- Don't recompute invariants inside loops; don't load more data than needed.
- Stream or batch large inputs instead of materializing everything.

These are habits, not optimizations. Anything that makes code harder to read needs evidence.

### 4. Optimize only with evidence
When the user asks for performance work, or a hot path is evident:
1. **Establish a baseline**: identify what to measure and how (profiler, benchmark, query plan, timing). If you can run code, measure; if you can't, say the claim is unmeasured.
2. **Find the bottleneck**: algorithmic complexity and I/O dominate. Micro-optimizations rarely matter.
3. **Fix the biggest cost first**, in this order: algorithm/data structure, then I/O and network (batching, caching, concurrency), then memory/allocation, then language-level tweaks.
4. **Re-measure** and report the result honestly. If it didn't help, revert.
5. **Document the trade-off** in a brief comment when the optimized code is less obvious than the naive version, so nobody "simplifies" it back.

Never claim a speedup you haven't measured or can't justify with complexity analysis. Say "should reduce this from O(n²) to O(n log n)", not "much faster".

### 5. Protect behavior
- Preserve existing behavior during refactors unless told otherwise. Don't change public interfaces, output formats, or error semantics silently.
- Run existing tests if possible. When changing logic, add or update tests that pin down the behavior, especially edge cases (empty input, nulls, boundaries, large inputs, concurrency).
- Refactor and change behavior in separate steps, so problems are easy to localize.

## Before you finish: checklist

- [ ] Does it do what was asked, including edge cases and failure paths?
- [ ] Could a new teammate understand each function in under a minute?
- [ ] Any quadratic-or-worse loops, N+1 calls, or repeated work that could be trivially avoided?
- [ ] Are names, style, and structure consistent with the surrounding code?
- [ ] Are errors handled explicitly, with no silent failures or leaked resources (files, connections, locks)?
- [ ] No secrets, debug leftovers, dead code, or commented-out blocks?
- [ ] Is every optimization measured or justified, and every non-obvious choice explained?
- [ ] Are tests present or updated for new or changed logic?

## How to report your work

Keep the summary short and useful to the reviewer:
- What changed and why, in a few sentences.
- Any trade-offs or assumptions (e.g. "used a dict for O(1) lookup; uses more memory").
- Measured results if you optimized; otherwise label estimates as estimates.
- Notable issues you noticed but deliberately left alone.

Don't pad with a lecture on best practices. Show the improvement in the code and explain only the non-obvious decisions.

## Anti-patterns to avoid

- **Premature optimization**: complex caching, bit tricks, or manual loop unrolling with no measurement.
- **Over-engineering**: factories, plugin systems, or config layers for a problem that has one case today.
- **Clever code**: dense one-liners, nested ternaries, or obscure idioms that save lines but cost comprehension.
- **Drive-by rewrites**: restyling or reorganizing code unrelated to the request, which bloats the diff and hides real changes.
- **Cargo-cult patterns**: applying a pattern (or a language idiom) because it's fashionable rather than because it fits.
- **Stale comments**: a wrong comment is worse than none. Update or delete when code changes.
