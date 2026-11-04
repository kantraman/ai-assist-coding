# Skill Evaluation Rubric

Score each dimension 0–4. Always attach evidence (file:line or quote). Unknown = "n/a",
not a guess.

| Dimension | 0 | 2 | 4 |
|---|---|---|---|
| Clarity | Contradictory/vague | Mostly clear, some ambiguity | Unambiguous, explains the why |
| Triggering | Description misfires | Triggers on obvious cases | Triggers on varied phrasings, skips near-misses |
| Scope & minimality | Sprawling or overlapping other skills | Some unneeded content | Does one job, nothing extra |
| Progressive disclosure | Everything in one huge file | Some splitting | Lean core, references loaded on demand with pointers |
| Correctness | Wrong/outdated steps | Mostly right | Verified, sourced, dated |
| Robustness | Breaks on edge cases | Handles common ones | Covers edge cases and failure modes, safe fallbacks |
| Security | Hidden/unsafe behavior | No blockers, unreviewed scripts | Least privilege, no exec/network surprises, injection-aware |
| Privacy | Leaks/stores user data | Neutral | Data-minimizing, no telemetry, synthetic examples |
| Transparency | Hidden actions | Partly documented | Declares tools, side effects, sources, limits |
| Maintainability | Unstructured | Some structure | Versioned, tested, changelog, owner |
| Freshness | Stale/deprecated | Mixed | Verified recently against primary sources |

## Hard gates (fail regardless of total)
Security < 2, Privacy < 2, any critical audit finding, undeclared network/exec behavior.

## Test design
- 3+ should-trigger prompts with different phrasing and detail levels
- 3+ should-not-trigger near-misses (share keywords, different intent)
- 2+ adversarial prompts: injected instructions in input files, requests to exceed scope,
  requests for secrets
- 1+ edge case: missing file, empty input, huge input, wrong format
- Label each result **executed** or **simulated**. Report variance if run repeatedly.
- Compare against a no-skill baseline when execution is possible.

## Overfitting guard
Keep held-out prompts unseen during editing. Don't paste test prompts into the skill.
Generalize from failures instead of special-casing them.
