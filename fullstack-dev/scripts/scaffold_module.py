#!/usr/bin/env python3
"""Scaffold a fractal module: contract/, core/, adapters/, tests/ plus module.json (stdlib only)."""
import argparse
import json
import os
import re
import sys

LAYERS = ["ui", "api", "domain", "data", "shared"]
README = """# {name}

Layer: {layer}

## Contract
What this module promises (types, ports, events, errors). Other modules depend only on `contract/`.

## Core
Pure logic, no I/O, deterministic.

## Adapters
All I/O and framework glue, implementing the ports declared in the contract.

## Proof
Tests in `tests/`, requirements in `module.json`. Update the manifest in the same commit as code changes.

Budgets: (latency / size / error rate for this module)
"""


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("name", help="module id (letters, digits, - _ .)")
    p.add_argument("--layer", choices=LAYERS, default="domain")
    p.add_argument("--root", default="src/modules")
    p.add_argument("--ext", default="txt", help="stub file extension, e.g. ts, py, java, go")
    p.add_argument("--requirement", action="append", default=[], help="requirement id this module implements")
    a = p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", a.name):
        sys.exit("invalid module name")
    base = os.path.join(a.root, a.name)
    if os.path.exists(base):
        sys.exit(f"{base} already exists; refusing to overwrite")
    for d in ("contract", "core", "adapters", "tests"):
        os.makedirs(os.path.join(base, d))
        with open(os.path.join(base, d, f".gitkeep"), "w"):
            pass
    stubs = {
        "contract": "Contract: types, ports (interfaces), events, error types.",
        "core": "Core: pure functions. No I/O, no framework imports, no env access.",
        "adapters": "Adapters: implement ports (DB, HTTP, queue). Keep thin.",
        "tests": "Tests: unit (core), contract, integration (adapters).",
    }
    for d, text in stubs.items():
        with open(os.path.join(base, d, f"README.{a.ext if a.ext != 'txt' else 'md'}"), "w") as f:
            f.write(text + "\n")
    edges = [{"rel": "implements", "to": r} for r in a.requirement]
    edges.append({"rel": "tested_by", "to": f"{a.name}.unit"})
    manifest = {"id": a.name, "type": "Module", "layer": a.layer,
                "nodes": [{"id": f"{a.name}.unit", "type": "Test"}], "edges": edges}
    with open(os.path.join(base, "module.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    with open(os.path.join(base, "README.md"), "w") as f:
        f.write(README.format(name=a.name, layer=a.layer))
    print(f"created {base} (layer={a.layer}); declare depends_on/exposes/persists edges in module.json")


if __name__ == "__main__":
    main()
