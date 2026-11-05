# fullstack-dev

A portable skill for full stack development in any coding agent: database schema, API, frontend UX, tests, security, and performance, using fractal modular architecture, genetic-algorithm tuning, and a knowledge graph with an ontology.

It uses the open `SKILL.md` format (a folder with `SKILL.md`, `references/`, `scripts/`, `assets/`). The scripts are stdlib-only Python 3.8+.

## Install

From the skill folder (or the unzipped archive):

```bash
# One neutral location read by several agents (project scope)
python3 scripts/install.py --agent neutral --project-dir /path/to/your/project

# Agent-specific folders
python3 scripts/install.py --agent claude      # .claude/skills/
python3 scripts/install.py --agent cursor      # .cursor/skills/
python3 scripts/install.py --agent copilot     # .github/skills/
python3 scripts/install.py --agent gemini      # .gemini/skills/
python3 scripts/install.py --agent neutral --agent claude --scope user   # in your home directory

# Any other agent that has a skills directory
python3 scripts/install.py --dest /path/to/that/skills/dir

# Agents without skill support: add an instructions block
python3 scripts/install.py --rules-file AGENTS.md       # or GEMINI.md, CONVENTIONS.md, .clinerules
python3 scripts/install.py --cursor-rule                # .cursor/rules/fullstack-dev.mdc
```

Add `--dry-run` to preview, `--link` to symlink instead of copy, `--uninstall` to remove. The installer only deletes directories it can identify as this skill, and the instructions block is wrapped in markers so re-running replaces it instead of duplicating it.

Agent conventions change quickly. If an agent does not pick the skill up, check its documentation for its skills path and use `--dest`, or point it at `SKILL.md` directly ("read fullstack-dev/SKILL.md and follow it").

## Use

Ask in plain language, naming the stack: "Build a bookings app with Next.js and Postgres", "Add multi-tenancy to this FastAPI service", "Tune our API cache and pool settings against this benchmark".

## Contents

- `SKILL.md`: workflow, technique gates, capability fallbacks
- `references/`: fractal architecture, genetic optimization, knowledge graph, DB, API, frontend UX, quality gates, stack profiles
- `scripts/`: `kg_build.py`, `ga_tuner.py`, `scaffold_module.py`, `design_tokens.py`, `install.py`
- `assets/`: `ontology.json`, `module.template.json`
- `adapters/`: `rules-snippet.md` used for instruction-file installs
