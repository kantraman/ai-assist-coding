# Genetic Optimization

Genetic algorithms (GA) search large spaces of interacting choices by evolving a population of candidates against a fitness score. In full stack work they are a precision tool for **measurable, multi-parameter tuning**, plus a lightweight qualitative variant for design decisions.

## Contents
1. Decide: GA, tournament, or just measure
2. What makes a good genome
3. Fitness design
4. Procedure with `ga_tuner.py`
5. Config reference
6. Qualitative design tournament
7. Pitfalls

## 1. Decide

| Situation | Use |
|---|---|
| One obvious bottleneck (missing index, N+1, huge payload) | Fix it directly; measure before and after |
| 1 to 2 tunables | Grid or manual sweep |
| 3+ interacting tunables, a repeatable benchmark, a cheap-enough run (seconds, not hours) | **ga_tuner.py** |
| Architecture, schema shape, API shape (no numeric benchmark) | **Design tournament** (section 6) |
| Correctness, security | Never optimize these; they are gates |

## 2. Genome candidates

Good genes are bounded, independent of correctness, and affect measurable outcomes:

- **DB**: which optional indexes exist (bool per index), composite column order (choice), fillfactor, connection pool size, statement timeout, batch insert size.
- **Cache**: TTL per resource class, max entries, eviction policy (choice), stale-while-revalidate window.
- **API**: page size, compression threshold, ETag on/off, batch endpoint chunk size.
- **Runtime**: worker count, queue concurrency, retry backoff base/cap, keep-alive.
- **Frontend**: bundle chunk split strategy, image quality and widths, prefetch on hover (bool), virtualization window size, debounce ms.

Encode as `int`, `float`, `choice`, or `bool`. Keep the genome under about 12 genes; search cost grows quickly.

## 3. Fitness design

- **Gates first** (hard constraints): tests pass, error rate under X%, memory under budget, no security checks regressed. A candidate that fails a gate is invalid, not "slightly worse".
- **Objectives** (weighted): p95 latency (min), throughput (max), memory (min), cost (min), bundle KB (min). Give each a `scale` (typical magnitude) so weights are comparable.
- **Realistic workload**: replay representative traffic or data shapes. Tuning to a toy workload overfits.
- **Noise**: use `repeats` (median) and compare the final winner against baseline several times. Improvements inside the noise band do not count.
- **Goodhart's law**: if one metric can be gamed (cache everything, return stale data), add a gate for the thing it would sacrifice.
- **Holdout**: validate the winner on a workload the search never saw.

## 4. Procedure

1. Record a **baseline** genome and its metrics (the current production values).
2. Write a benchmark command that reads genes from environment variables `GENE_<NAME>` (uppercased) and prints one JSON object of metrics on its last stdout line, for example `{"p95_ms": 182, "rps": 940, "errors": 0}`. Non-zero exit or timeout = invalid candidate.
3. Write the config (section 5) and run:
   ```bash
   python scripts/ga_tuner.py --config tuning/api.json --out tuning/api.result.json
   ```
4. Inspect `history` (did it converge or plateau?) and `top` (are several distinct genomes close? then the surface is flat and the choice can favor simplicity).
5. Re-run the best genome and the baseline at least 5 times on the holdout workload. Adopt only if the gain exceeds the noise and the margin you set (suggest 5% or more).
6. Commit the genome to `tuning/`, write an ADR (what, why, measured gain, workload), and add a regression check to CI so drift is caught.
7. Re-tune when workload, data volume, or hardware changes materially.

## 5. Config reference (`ga_tuner.py`)

```json
{
  "genes": [
    {"name": "pool_size",  "type": "int",    "min": 5,  "max": 80},
    {"name": "cache_ttl",  "type": "int",    "min": 5,  "max": 600},
    {"name": "page_size",  "type": "choice", "choices": [25, 50, 100, 200]},
    {"name": "compress",   "type": "bool"},
    {"name": "backoff",    "type": "float",  "min": 0.05, "max": 2.0}
  ],
  "command": ["python", "bench/run_api_bench.py"],
  "timeout_s": 120,
  "repeats": 3,
  "objectives": [
    {"metric": "p95_ms", "direction": "min", "weight": 1.0, "scale": 200},
    {"metric": "rps",    "direction": "max", "weight": 0.5, "scale": 1000}
  ],
  "gates": [
    {"metric": "errors", "op": "<=", "value": 0}
  ],
  "baseline": {"pool_size": 20, "cache_ttl": 60, "page_size": 50, "compress": false, "backoff": 0.2},
  "population": 20, "generations": 15, "elite": 2, "tournament": 3,
  "crossover_rate": 0.8, "mutation_rate": 0.15, "patience": 5, "workers": 1, "seed": 42
}
```

Run benchmarks with `workers: 1` unless runs are isolated; parallel runs on one machine contaminate latency numbers.

## 6. Design tournament (qualitative GA)

For schema, API, or architecture choices with no numeric benchmark. Mirrors GA, run in the conversation:

1. **Population (3 to 5 candidates)**: deliberately different designs, for example normalized vs. hybrid JSONB schema, REST vs. RPC-style API, modular monolith vs. two services.
2. **Fitness rubric**: score each 1 to 5 on accuracy, security, testability, maintainability, scalability, performance, flexibility, evolution, weighted by the user's stated priorities. Use evidence (query plans, expected volume, team size), not vibes. Any candidate violating a gate is eliminated.
3. **Selection**: keep the top two.
4. **Crossover**: combine the best traits (the winner's structure plus the runner-up's strength).
5. **Mutation**: attack the weakest rubric score of the child and revise.
6. **Stop** after two rounds or when the winner is clear. Record the decision and the losing options with reasons in an ADR so the choice can be revisited when constraints change.

Show the scoring table briefly; do not narrate every step.

## 7. Pitfalls

- Tuning before profiling. Evolutionary search is not a substitute for finding the actual bottleneck.
- Too-wide ranges that produce nonsense candidates; bound genes by what the system can safely run.
- Over-trusting one run. Stochastic search plus noisy benchmarks needs repeated validation.
- Leaving tuned values undocumented; the next engineer will "clean them up".
