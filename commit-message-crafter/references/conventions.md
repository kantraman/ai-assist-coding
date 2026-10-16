# Commit message conventions and examples

## Contents
- Conventional Commit types
- Choosing a scope
- Before / after examples
- Anti-patterns
- Subject-line verbs
- Breaking changes and footers

## Conventional Commit types

Format: `type(scope)!: subject`. Scope and `!` are optional.

| Type | Use when | Not when |
|---|---|---|
| `feat` | Users/callers gain new capability | Internal helper added only to support a refactor |
| `fix` | Behaviour was wrong and now is right | Behaviour was fine but code was cleaned up (`refactor`) |
| `refactor` | Structure changes, behaviour doesn't | Any observable behaviour change |
| `perf` | Measurable speed/memory improvement is the point | Incidental speedup from a refactor |
| `docs` | Only docs, comments-as-docs, README | Docstring edits bundled with code changes (use the code's type) |
| `test` | Only tests added/changed | Tests added alongside the feature/fix they cover (use that type) |
| `build` | Dependencies, build tooling, packaging, Dockerfile | CI pipeline files (`ci`) |
| `ci` | CI/CD config and workflows | |
| `style` | Whitespace, formatting, lint-only, no logic change | Renames or restructures (`refactor`) |
| `chore` | Maintenance that fits nowhere else (version bumps, housekeeping) | Anything user-visible |
| `revert` | Reverting an earlier commit; body names the SHA and reason | |

Deciding between `feat` and `fix`: ask "did this ever work as intended?" If the old behaviour was a defect, it's `fix`. If the capability never existed, it's `feat`. When tests encode a regression, that's usually a `fix`.

## Choosing a scope

A scope is the part of the codebase a reader would search by: a module, package, service, or feature area. Pick the narrowest name that covers the whole change.

- Prefer names that already appear in recent history (the analyzer's `common types` and examples help). Consistency matters more than perfection.
- Use the directory/package for monorepos (`api`, `web`, `billing`), or the feature area in apps (`auth`, `checkout`).
- Omit the scope when the change spans many areas or the repo is small. A wrong scope is worse than none.
- Don't use file names or ticket ids as scopes.

## Before / after examples

**Vague → specific**
- Before: `fix bug`
- After: `fix(parser): handle empty input without raising IndexError`

**Describes the diff → describes the intent**
- Before: `change timeout from 30 to 120 in client.py`
- After: `fix(client): raise request timeout to 120s for large exports`
  Body: `Exports over ~50k rows regularly exceeded 30s and failed with a retry storm. ...`

**Missing why → includes why**
- Before: `refactor: move validation into separate module`
- After:
  ```
  refactor(orders): extract validation into orders.validation

  The create and update handlers each carried a near-identical copy of the
  validation rules and had already drifted (update allowed zero quantity).
  Both now call the shared validators. No behaviour change intended.
  ```

**Multiple concerns → split**
- Mixed: formatter re-run over 40 files + one real bug fix in `retry.py`
- Better: commit 1 `style: apply black formatting`, commit 2 `fix(retry): stop retrying on 4xx responses`. The fix is now reviewable and revertable on its own.

**Past tense / noise → imperative / signal**
- Before: `Updated files and fixed some stuff.`
- After: `fix(upload): reject files over the configured size limit`

**Trivial change stays trivial**
- `docs: fix typo in installation steps` (no body needed)
- `chore: bump version to 2.4.1`

## Anti-patterns

- **Single-word or generic subjects**: "fix", "update", "wip", "changes", "misc"
- **Restating file names** instead of behaviour: "edit utils.py and app.js"
- **Narrating the edit** in the body ("I changed the loop to...") rather than explaining reasoning
- **"Fix review comments" / "address feedback"**: say what was actually fixed, or squash before merge
- **Overclaiming**: "fix race condition" when the change only reduces its likelihood; say so ("reduce")
- **Invented motivation**: stating a cause or benefit the diff doesn't support
- **Kitchen-sink commits**: "and" in the subject usually means two commits
- **Giant subject lines**: if you can't fit it in ~72 chars, the detail belongs in the body

## Subject-line verbs

Good imperative verbs and what they imply: `add` (new thing), `remove` (deleted), `fix` / `prevent` / `handle` (defect), `reject` / `validate` (guarding), `rename` / `move` / `extract` / `inline` (structure), `replace` / `switch` (swap implementation), `reduce` / `speed up` / `cache` (performance), `bump` / `pin` / `drop` (dependencies), `document` / `clarify` (docs), `allow` / `support` / `enable` (capability), `deprecate` (signalling removal).

Avoid `update` and `change` unless nothing more precise is true; they say nothing about direction.

## Breaking changes and footers

Signal a breaking change in both places:

```
feat(api)!: require API version header on all requests

Requests without `X-Api-Version` previously defaulted to v1. Defaulting
hid client misconfiguration and blocked removal of v1 routes.

BREAKING CHANGE: clients must send `X-Api-Version`. Requests without it
now receive 400. Set the header to `1` to keep current behaviour.
```

Common footers (match the host and repo style):
- `Fixes #123`, `Closes #123`: auto-closes the issue on merge
- `Refs PROJ-456` / `Related-to: #99`: link without closing
- `Co-authored-by: Name <email>`: only when the user says there are co-authors
- `Reviewed-by:`, `Signed-off-by:`: only if the repo uses them (DCO projects require sign-off)

## Body guidelines

Structure that works for non-trivial changes, in order:
1. **Problem / context**: what was wrong or needed, in one or two sentences
2. **Approach**: what the change does at a conceptual level
3. **Trade-offs / alternatives**: why not the obvious other way, if relevant
4. **Impact**: migrations, config, behaviour changes, follow-up work

Wrap at ~72 columns. Use plain paragraphs; short `-` bullets are fine for a list of discrete changes in a larger commit. Don't use markdown headings in commit bodies.
