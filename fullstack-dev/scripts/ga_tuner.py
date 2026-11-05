#!/usr/bin/env python3
"""Generic genetic-algorithm tuner for measurable parameters (stdlib only).

The benchmark command receives genes as env vars GENE_<NAME> (uppercase) and a
GENOME_JSON var, and must print a JSON object of metrics on its LAST stdout line.
Non-zero exit, timeout, bad JSON, or a failed gate makes the candidate invalid.

Usage:
  ga_tuner.py --config tuning/cfg.json [--out result.json]
  ga_tuner.py --demo          # built-in self-test with a synthetic benchmark
See references/genetic-optimization.md for the config format.
"""
import argparse
import json
import math
import os
import random
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

INVALID = -1e18
OPS = {"<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b, "<": lambda a, b: a < b,
       ">": lambda a, b: a > b, "==": lambda a, b: a == b}


def rand_gene(g, rng):
    t = g["type"]
    if t == "int":
        return rng.randint(g["min"], g["max"])
    if t == "float":
        return rng.uniform(g["min"], g["max"])
    if t == "choice":
        return rng.choice(g["choices"])
    if t == "bool":
        return rng.random() < 0.5
    raise ValueError(f"unknown gene type {t}")


def mutate_gene(g, v, rng, strength):
    t = g["type"]
    if t == "int":
        span = max(1, g["max"] - g["min"])
        nv = v + int(round(rng.gauss(0, span * 0.15 * strength)))
        if nv == v:
            nv = v + rng.choice([-1, 1])
        return min(g["max"], max(g["min"], nv))
    if t == "float":
        span = g["max"] - g["min"]
        return min(g["max"], max(g["min"], v + rng.gauss(0, span * 0.15 * strength)))
    if t == "choice":
        others = [c for c in g["choices"] if c != v]
        return rng.choice(others) if others else v
    if t == "bool":
        return not v
    return v


def key(genome):
    return json.dumps(genome, sort_keys=True, default=str)


def round_genome(genes, genome):
    out = {}
    for g in genes:
        v = genome[g["name"]]
        out[g["name"]] = round(v, 6) if g["type"] == "float" else v
    return out


def run_once(cfg, genome):
    env = dict(os.environ)
    for k, v in genome.items():
        env["GENE_" + k.upper()] = str(v).lower() if isinstance(v, bool) else str(v)
    env["GENOME_JSON"] = json.dumps(genome)
    cp = subprocess.run(cfg["command"], env=env, capture_output=True, text=True,
                        timeout=cfg.get("timeout_s", 120), cwd=cfg.get("cwd"))
    if cp.returncode != 0:
        raise RuntimeError(f"exit {cp.returncode}: {cp.stderr.strip()[:200]}")
    lines = [ln for ln in cp.stdout.strip().splitlines() if ln.strip()]
    if not lines:
        raise RuntimeError("no output")
    return json.loads(lines[-1])


def demo_bench(genome):
    # Synthetic: best near pool=32, ttl=180, page=100, compress on. Includes noise.
    p, t, pg, c = genome["pool_size"], genome["cache_ttl"], genome["page_size"], genome["compress"]
    lat = 40 + 0.08 * (p - 32) ** 2 + 0.002 * (t - 180) ** 2 + abs(pg - 100) * 0.4 - (12 if c else 0)
    lat += random.gauss(0, 0.5)
    rps = 1200 - 2.0 * abs(p - 32) - 0.5 * abs(t - 180) - abs(pg - 100) * 0.8
    return {"p95_ms": lat, "rps": rps, "errors": 0 if p < 70 else 3}


def evaluate(cfg, genome):
    repeats = cfg.get("repeats", 1)
    samples = []
    try:
        for _ in range(repeats):
            m = demo_bench(genome) if cfg["command"] == "__demo__" else run_once(cfg, genome)
            samples.append(m)
    except Exception as e:  # noqa: BLE001
        return INVALID, {"error": str(e)}
    metrics = {}
    for k in samples[0]:
        vals = [s[k] for s in samples if isinstance(s.get(k), (int, float))]
        if vals:
            metrics[k] = statistics.median(vals)
    for gate in cfg.get("gates", []):
        v = metrics.get(gate["metric"])
        if v is None or not OPS[gate["op"]](v, gate["value"]):
            return INVALID, {**metrics, "gate_failed": gate["metric"]}
    score = 0.0
    for o in cfg["objectives"]:
        v = metrics.get(o["metric"])
        if v is None:
            return INVALID, {**metrics, "missing_metric": o["metric"]}
        sign = -1.0 if o["direction"] == "min" else 1.0
        score += o.get("weight", 1.0) * sign * v / o.get("scale", 1.0)
    return score, metrics


def tournament(pop, scores, k, rng):
    picks = rng.sample(range(len(pop)), min(k, len(pop)))
    return pop[max(picks, key=lambda i: scores[i])]


def diversity(pop, genes):
    if len(pop) < 2:
        return 0.0
    keys = {key(g) for g in pop}
    return len(keys) / len(pop)


def run_ga(cfg, log=print):
    rng = random.Random(cfg.get("seed"))
    random.seed(cfg.get("seed"))
    genes = cfg["genes"]
    pop_n = cfg.get("population", 20)
    gens = cfg.get("generations", 15)
    elite = cfg.get("elite", 2)
    tk = cfg.get("tournament", 3)
    cx = cfg.get("crossover_rate", 0.8)
    mut = cfg.get("mutation_rate", 0.15)
    patience = cfg.get("patience", 5)
    workers = cfg.get("workers", 1)
    cache = {}
    evals = [0]

    def score_all(pop):
        todo = [g for g in pop if key(g) not in cache]
        todo = list({key(g): g for g in todo}.values())

        def one(g):
            return key(g), evaluate(cfg, g)

        if workers > 1:
            with ThreadPoolExecutor(max_workers=workers) as ex:
                for k, res in ex.map(one, todo):
                    cache[k] = res
        else:
            for g in todo:
                k, res = one(g)
                cache[k] = res
        evals[0] += len(todo)
        return [cache[key(g)][0] for g in pop]

    result = {"baseline": None}
    if cfg.get("baseline"):
        b = round_genome(genes, cfg["baseline"])
        bs, bm = evaluate(cfg, b)
        cache[key(b)] = (bs, bm)
        result["baseline"] = {"genome": b, "score": bs, "metrics": bm}
        log(f"baseline score={bs:.4f} metrics={bm}")

    pop = [round_genome(genes, {g["name"]: rand_gene(g, rng) for g in genes}) for _ in range(pop_n)]
    if cfg.get("baseline"):
        pop[0] = round_genome(genes, cfg["baseline"])  # seed with the known-good design
    history, best_score, stall = [], INVALID, 0
    strength = 1.0
    for gen in range(gens):
        scores = score_all(pop)
        order = sorted(range(len(pop)), key=lambda i: scores[i], reverse=True)
        top = scores[order[0]]
        valid = [s for s in scores if s > INVALID]
        history.append({"generation": gen, "best": top,
                        "mean": (sum(valid) / len(valid)) if valid else None,
                        "valid": len(valid), "diversity": round(diversity(pop, genes), 2)})
        log(f"gen {gen:>2}: best={top:.4f} valid={len(valid)}/{len(pop)} diversity={history[-1]['diversity']}")
        if top > best_score + 1e-9:
            best_score, stall = top, 0
        else:
            stall += 1
        if stall >= patience:
            log(f"no improvement for {patience} generations; stopping early")
            break
        strength = 2.0 if diversity(pop, genes) < 0.5 else 1.0  # push exploration if converged
        nxt = [pop[i] for i in order[:elite]]
        while len(nxt) < pop_n:
            a, b = tournament(pop, scores, tk, rng), tournament(pop, scores, tk, rng)
            child = {}
            for g in genes:
                n = g["name"]
                child[n] = (a if rng.random() < 0.5 else b)[n] if rng.random() < cx else a[n]
                if rng.random() < mut:
                    child[n] = mutate_gene(g, child[n], rng, strength)
            nxt.append(round_genome(genes, child))
        pop = nxt

    ranked = sorted(cache.items(), key=lambda kv: kv[1][0], reverse=True)
    seen, top_list = set(), []
    for k, (s, m) in ranked:
        if s <= INVALID or k in seen:
            continue
        seen.add(k)
        top_list.append({"genome": json.loads(k), "score": s, "metrics": m})
        if len(top_list) >= 5:
            break
    result.update({"best": top_list[0] if top_list else None, "top": top_list,
                   "history": history, "evaluations": evals[0]})
    if result["baseline"] and result["best"] and result["baseline"]["score"] > INVALID:
        bs, ns = result["baseline"]["score"], result["best"]["score"]
        result["improvement_vs_baseline"] = ns - bs
        result["note"] = ("Score deltas are in objective units. Re-run best and baseline several times on a "
                          "holdout workload before adopting; ignore gains inside measurement noise.")
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config")
    ap.add_argument("--out")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.demo:
        cfg = {
            "genes": [{"name": "pool_size", "type": "int", "min": 5, "max": 80},
                      {"name": "cache_ttl", "type": "int", "min": 5, "max": 600},
                      {"name": "page_size", "type": "choice", "choices": [25, 50, 100, 200]},
                      {"name": "compress", "type": "bool"}],
            "command": "__demo__", "repeats": 1,
            "objectives": [{"metric": "p95_ms", "direction": "min", "weight": 1.0, "scale": 100},
                           {"metric": "rps", "direction": "max", "weight": 0.5, "scale": 1000}],
            "gates": [{"metric": "errors", "op": "<=", "value": 0}],
            "baseline": {"pool_size": 20, "cache_ttl": 60, "page_size": 50, "compress": False},
            "population": 20, "generations": 20, "seed": 7, "patience": 6}
    elif a.config:
        cfg = json.load(open(a.config, encoding="utf-8"))
    else:
        ap.error("provide --config or --demo")
    t0 = time.time()
    res = run_ga(cfg, log=lambda s: print(s, file=sys.stderr))
    res["seconds"] = round(time.time() - t0, 1)
    text = json.dumps(res, indent=2, default=str)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"wrote {a.out}", file=sys.stderr)
    best = res.get("best")
    if best:
        print("best genome:", json.dumps(best["genome"]))
        print("metrics:", json.dumps(best["metrics"]))
        if res.get("improvement_vs_baseline") is not None:
            print(f"improvement vs baseline (objective units): {res['improvement_vs_baseline']:.4f}")
    else:
        print("no valid candidate found (all failed gates or errored)", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
