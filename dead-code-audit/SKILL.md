---
name: dead-code-audit
description: Find out whether code is actually in use or is leftover junk that should be removed in a refactor. Maps internal dependencies (who imports/calls what), detects dead code (unreferenced files, functions, classes, exports, unused third-party packages, stale feature flags, commented-out blocks), rates each finding by confidence, and prepares safe removals that can be restored from git. Use this skill whenever the user mentions dead code, unused code, unused imports/dependencies, orphan files, cleanup, "is this still used", "can I delete this", refactor prep, codebase bloat, legacy leftovers, or asks what depends on a module or function, even if they never say "dead code".
---

# Dead Code Audit

Goal: for every candidate, answer "is this code in use, or is it junk?" with evidence, then
(only if asked) remove it in a way that git can fully undo.

Deleting live code is far costlier than leaving dead code for another week, so every
finding carries a confidence level and the reasoning behind it. Static analysis cannot see
reflection, dependency injection, string-based lookups, framework conventions, or callers
outside the repo; those blind spots are where wrong deletions come from. Treat them
explicitly rather than hoping they don't apply.

## Workflow

### 1. Scope and ground rules
- Confirm the target: whole repo, a directory, or specific files/symbols. Default to the whole repo, read-only.
- Run `git status`. If the tree is dirty, say so; removals need a clean base so they can be reverted cleanly.
- Identify languages, frameworks, and entry points (see step 2). Read `references/tool-matrix.md` for the languages present.
- Default mode is **report only**. Do not delete anything until the user asks.

### 2. Establish the roots (what is "in use" by definition)
Dead code is code unreachable from the roots. Wrong roots produce wrong answers, so list them
before analyzing: `main`/CLI entry points, `package.json` (`main`, `bin`, `exports`, scripts),
`pyproject.toml`/`setup.py` entry points, web routes/handlers, serverless handlers, cron/job
registrations, migrations, test files, build/config files (webpack, jest, Dockerfile, CI),
and the public API if this is a library (exported symbols may have external callers, so they
are not dead merely because nothing in this repo calls them).

### 3. Run the quick scan
```bash
python scripts/scan.py <repo-root> --format md > /tmp/dead-code-scan.md
```
Stdlib-only; works on Python and JS/TS (and degrades to word-level reference counting for
other languages). It reports orphan files (nothing imports them), top-level symbols with
no references, test-only symbols, and the last commit date touching each. Use it as the
candidate generator, not the verdict.

For depth, also run the language's dedicated tool from `references/tool-matrix.md`
(vulture, knip, deadcode, cargo-udeps, etc.) if installed. Tools disagree at the margins; agreement
between the scan and a dedicated tool raises confidence.

### 4. Verify each candidate
For each candidate, collect evidence in this order:
1. **Static references**: `git grep -n -w <name>` (also the file's module path / basename). Separate production references, test-only references, and comments/docs.
2. **Dynamic references**: search for the name inside strings, config files (YAML/JSON/TOML/INI), templates, SQL, shell scripts, Dockerfiles, CI files, and docs. Also check for `getattr`, `importlib`, `require(variable)`, `import()`, reflection, decorators/registries, DI containers, serialization class names, ORM models, and plugin loaders.
3. **Framework conventions**: files or names the framework loads by position or naming (Next.js `pages/`, Django `admin.py`/`models.py`/management commands, pytest fixtures/`conftest.py`, Rails/Spring autoloading, lifecycle methods, `__init__`, dunder methods, interface implementations).
4. **History**: `git log -1 --format=%cs -- <file>` and `git log --oneline -5 -S<name>`. Untouched for a long time plus zero references is supporting evidence; recently added with zero references may be work-in-progress.
5. **Runtime evidence, if the user has it**: coverage reports, APM/logging, feature-flag dashboards. Mention it as the strongest confirmation available and ask only if the call is genuinely risky.

### 5. Classify with confidence
| Level | Meaning | Typical evidence |
|---|---|---|
| **High** | Safe to remove | Zero refs anywhere (code, strings, config, docs); not a root; not exported publicly; no framework convention; confirmed by a dedicated tool |
| **Medium** | Probably dead, verify | Zero static refs but possible dynamic use; or referenced only by tests/other dead code; or exported from a library |
| **Low** | Do not remove without a human check | Matches a framework convention, referenced in strings/config, plugin/registry pattern, recently added |
| **Live** | In use | Reachable from a root. Record who depends on it. |

Dead code often hides in chains: A is used only by B, and B is dead. After the first pass,
re-run the analysis treating confirmed-dead items as removed, until nothing new appears.
Tell the user when removals cascade.

### 6. Report
Use this structure:

```
# Dead code audit: <repo/scope>
Summary: N candidates (X high, Y medium, Z low). Estimated removable: ~L lines / F files.
Roots assumed: ...
Tools used: ...

## High confidence (safe to remove)
| Item | Kind | Evidence | Last touched | Lines |
## Medium confidence (verify first)
| Item | Kind | Why uncertain | What would confirm it |
## Low confidence / keep
| Item | Why it looks dead but probably isn't |
## Dependencies
- Unused third-party packages: ...
- Missing/undeclared imports: ...
- Internal dependency hot spots (most depended-on modules) and cycles: ...
## Blind spots
What static analysis could not see in this repo.
```

When the user asked "what depends on X", answer with the dependents list (direct and
transitive), split into production and test, rather than the full report.

### 7. Remove (only when asked)
Follow `references/removal-and-restore.md`. In short: work on a branch, one commit per logical
group (e.g. "orphan files", "unused functions in billing/", "unused deps"), run
tests/build/lint after each commit, and write restore commands into every commit message.
Because the code stays in git history, deleting is cheap to undo; still, never remove Low or
Medium items without the user's go-ahead, and never touch generated, vendored, or
third-party directories.

## Things that look dead but usually aren't
- Public library API, CLI flags, webhook/route handlers, migrations, and schema definitions.
- Anything referenced by string: plugin names, task names, component registries, serialized class names.
- Test helpers/fixtures, mocks, type-only declarations (`.d.ts`, `Protocol`, interfaces), side-effect imports (`import "./polyfill"`).
- Code gated by feature flags or environment variables that are off *here* but on elsewhere.
- Platform-specific branches (`win32`, mobile) not exercised by the current environment.

## Things that are usually junk
- Large commented-out blocks (git is the archive; flag these for deletion).
- Files named `*_old`, `*_backup`, `*.bak`, `copy of`, `v1` alongside a `v2`, with no references.
- Unreachable code after `return`/`raise`, constant-false branches, flags permanently on/off.
- Imports and variables never used; packages in the manifest never imported.
- TODO/"temporary" scaffolding long past its date.
