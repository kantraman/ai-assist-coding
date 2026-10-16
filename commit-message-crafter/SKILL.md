---
name: commit-message-crafter
description: Write clear, accurate git commit messages by analysing the actual code changes (staged diff, working tree, a commit, or a range). Use whenever the user asks for a commit message, says "what should I commit this as", wants to improve, reword, squash or amend a message, asks to review a diff before committing, wants a PR title/squash message, or pastes a diff or `git status`/`git diff` output. Also use when a commit looks too big or mixed and may need splitting. Use it even if the user just says "commit this" or "write a commit" without mentioning diffs or conventions.
---

# Commit Message Crafter

A good commit message tells a future reader **what changed and, more importantly, why**, so they can understand the change without re-reading the diff. Messages like "fix bug" or "update files" fail because they restate the obvious and omit the reasoning. This skill works by reading the real changes first, then writing a message that matches the repo's own conventions.

## Workflow

### 1. Gather the changes

If a git repo is available, run the analyzer from the repo root:

```bash
python /path/to/commit-message-crafter/scripts/analyze_changes.py            # staged changes (falls back to working tree)
python .../analyze_changes.py --commit HEAD                                  # reword an existing commit
python .../analyze_changes.py --range main..HEAD                             # PR title / squash message
python .../analyze_changes.py --json                                         # machine-readable
```

It reports: files and change kinds, size, inferred type/scope hints, the repo's existing message style (conventional commits? ticket prefixes? typical length?), the ticket id from the branch name, and warnings (mixed concerns, debug leftovers, possible secrets, conflict markers, possible breaking changes).

Treat its output as a map, not the answer. It cannot know intent.

If there is no repo access (user pasted a diff or described the change), work from what they gave you. If the paste is just a file list with no diff, ask for the diff or a one-line description of the goal, because guessing from filenames produces generic messages.

### 2. Read the diff for the important files

Run `git diff --cached` (or the matching command) on the files that carry the change, skipping lockfiles, snapshots and generated output. Work out:

- **What** behaviour changed (not which lines moved)
- **Why**: the bug, requirement, constraint, or motivation. Look in the branch name, ticket id, code comments, test names, and anything the user said. If the why is genuinely unknowable and matters, ask **one** short question. Otherwise state only what the diff supports. Never invent a motivation.
- **Impact**: user-visible effects, API or schema changes, migrations, config the reader must update

### 3. Decide: one commit or several?

A commit should be one logical change. Suggest splitting when the analyzer flags mixed concerns, or when you see unrelated things together (a refactor plus a feature, formatting churn plus a bug fix, dependency bumps plus code). Splitting makes review, revert and bisect easier. If splitting is warranted, propose the groups with the files in each and one message per group, and let the user choose. Don't refuse to write a message for the combined change; offer both.

### 4. Match the repo's conventions

Follow what `recent_style` in the analyzer output shows. If most recent subjects use Conventional Commits, use them. If they're plain imperative sentences, don't add `feat:` prefixes. If they carry ticket ids (`PROJ-123:`), include the one from the branch. If there's no clear convention, default to Conventional Commits (see `references/conventions.md` for types and scope guidance).

### 5. Write the message

**Subject line**
- Imperative mood, as if completing "If applied, this commit will ___": `Add`, `Fix`, `Remove`, not `Added` or `Fixes`
- About 50 characters, hard ceiling 72. No trailing period
- Say what the change does at the level of behaviour or intent, e.g. `fix(auth): reject expired refresh tokens`, not `update auth.py`
- Specific beats broad: name the thing affected

**Body** (include whenever the change isn't trivially self-explanatory)
- Blank line after the subject, wrapped at ~72 columns
- Lead with the problem or motivation, then the approach, then notable trade-offs or alternatives rejected
- Mention side effects, follow-ups, and anything a reviewer might otherwise question
- Skip play-by-play of edits ("changed X in file Y"): the diff already shows that

**Footer**
- `BREAKING CHANGE: <what breaks and how to migrate>` (and `!` after the type/scope in Conventional Commits)
- `Fixes #123` / `Refs PROJ-456` using the style the repo uses
- `Co-authored-by:` only if the user mentions co-authors

Tiny, obvious changes (typo, version bump) deserve a one-line subject with no body. Padding them is noise.

### 6. Self-check before presenting

- Would someone who hasn't seen the diff understand what changed and why?
- Is every claim supported by the diff? Remove anything speculative.
- Is the subject specific, imperative, ≤72 chars?
- Did you describe the change as a whole, not just the first file?
- Are any analyzer warnings (secrets, debug code, conflict markers) something to tell the user about **before** they commit?

## Output format

Give the recommended message in a code block ready to paste, then keep commentary short:

````
```
fix(cart): prevent duplicate line items on rapid double-click

Clicking "Add to cart" twice within the request window created two
line items because the handler wasn't guarded while the first request
was in flight. Disable the button until the response arrives and
dedupe by SKU server-side as a backstop.

Fixes #482
```
````

Then add, only if relevant: warnings found, a split suggestion, or one alternative subject when the type or scope is genuinely ambiguous. Don't list five variants; pick the best one and say why in a sentence if it isn't obvious.

Do not run `git commit` unless the user asks you to. If they do, use a heredoc or `-F` file so multi-line bodies survive intact.

## Rewording and amending

For `--commit REF` or a pasted old message: keep the facts, fix the framing. Point out what the old message lacked (missing why, vague subject, wrong tense) in a line, then give the improved version. If rewriting published history would be needed, mention that it requires a force-push and ask before suggesting it.

## PR titles and squash messages

For `--range`, synthesise across all commits: the subject names the overall outcome, the body groups the main changes and explains the why once. Don't concatenate individual commit subjects.

## Resources

- `scripts/analyze_changes.py`: diff analysis and repo-style detection
- `references/conventions.md`: Conventional Commit types, scope selection, before/after examples, and anti-patterns. Read it when choosing a type or scope, or when the user wants examples of what good looks like.
