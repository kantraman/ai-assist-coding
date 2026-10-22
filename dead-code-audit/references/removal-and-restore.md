# Removing code safely and restoring it from git

Removal happens only after the user approves specific items.

## Before
```bash
git status                      # must be clean, else stop and ask
git switch -c chore/remove-dead-code-$(date +%Y%m%d)
# run the project's baseline: tests, build, lint, type-check. Note failures that already exist.
```

## Remove in small, revertable commits
One commit per logical group, so any single group can be reverted without touching others:
1. Unused imports/variables, commented-out blocks (lowest risk)
2. Unused functions/classes/exports (private first, then exported)
3. Orphan files
4. Unused dependencies (manifest + lockfile together)

After each group: run tests/build/lint/type-check. If anything breaks, `git restore .` or
`git reset --hard HEAD` (this branch only) and downgrade that item's confidence to Low.

Use `git rm` for files so the deletion is staged and tracked.

## Commit message template
```
chore: remove unused <what> in <where>

Verified unreferenced: static refs 0, string/config refs 0, not an entry point.
Tool agreement: <vulture/knip/scan.py>. Last touched: <date>.

Restore:
  whole file : git checkout <THIS_COMMIT>^ -- path/to/file
  whole commit: git revert <THIS_COMMIT>
```
Replace `<THIS_COMMIT>` with the real SHA after committing (use `git commit --amend` only if
nothing has been pushed), or point to the branch name.

## Restoring later (give the user this cheat sheet in the final summary)
```bash
# find when a file or symbol was deleted
git log --diff-filter=D --oneline -- path/to/file
git log -S'function_name' --oneline            # commits that added/removed the symbol

# bring a deleted file back
git checkout <sha>^ -- path/to/file            # <sha> = the deleting commit
# undo a whole removal commit
git revert <sha>
# view old code without restoring
git show <sha>^:path/to/file
```

## Never remove without explicit sign-off
- Items rated Low or Medium; public API of a library; migrations; anything in generated, vendored, or third-party directories; code referenced from config or strings.
- If the repo is shared and the branch is long-lived, mention that other branches may still reference the removed code (merge conflicts) and that deployed services outside this repo may call it.
