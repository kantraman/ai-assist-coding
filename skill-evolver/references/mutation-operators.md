# Mutation Operators and Evolution Guardrails

## Operators (apply 1–2 per variant)
**Description / triggering**: broaden with trigger phrases; narrow to exclude near-misses;
add negative triggers; reorder so key use-cases come first.
**Structure**: split oversized file into references; merge fragmented references; reorder
workflow steps; add a table of contents; add decision tables for mode/format selection.
**Content**: replace rule walls with reasoning; add a worked example; add an edge-case
section; remove dead or duplicate instructions; convert prose to a checklist (or reverse).
**Tooling**: replace a manual step with a deterministic script; replace a script with
instructions if it is rarely used; swap an unsafe call for a safe one.
**Freshness**: update versions/APIs with sources; remove deprecated paths.
**Safety**: add confirmation gates; add injection-handling note; narrow permissions.
Safety mutations are always allowed. Capability-widening mutations need approval.

## Fitness
```
fitness = 0.5*test_pass_rate + 0.3*rubric_mean/4 + 0.1*brevity + 0.1*triggering_accuracy
gate:   security >= parent, privacy >= parent, no new high/critical findings
```
Adjust weights to the user's priorities, state them in the report, and keep them fixed
within a run.

## lineage.json schema
```json
{
  "skill": "name",
  "baseline_hash": "sha256...",
  "variants": [
    {"id": "g1-v2", "parent": "baseline", "operator": "add-edge-case-section",
     "diff_hash": "sha256...", "train": 0.71, "heldout": 0.68,
     "security_gate": "pass", "decision": "candidate|rejected|accepted",
     "notes": "why"}
  ]
}
```

## Guardrails
- Held-out prompts decide selection; train scores only guide generation.
- One concept per variant so causes are attributable.
- Reject variants that add hidden content, remove safeguards, or change purpose.
- Diversity: include at least one conservative variant (minimal edit) per generation.
- Budget: default 3 generations x 4 variants; stop on plateau.
- Human review of the final diff is mandatory before replacing the original.
- Keep all rejected variants' summaries in lineage; they are evidence, not clutter.
