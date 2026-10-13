# Refactor Playbook

Contents: 1. Safety net, 2. Finding problems, 3. Strategies for big changes,
4. Common moves, 5. Ordering rules, 6. Large mechanical changes, 7. Rollback.

## 1. Safety net first

A refactor is only safe if you can tell when behavior changed.

- **Tests exist and pass:** record the pass count in `PLAN.md` and use them after every batch.
- **Tests are weak or missing:** write *characterization tests* before refactoring. These pin down what the code does
  today, even if it looks wrong. Call the function/endpoint with several realistic inputs,
  save the outputs as the expected values. Do not "fix" behavior here; capture it.
- **Cannot test at all (UI-heavy, legacy):** write a manual checklist of 5 to 15 user actions in `PLAN.md`
  and ask the user to run it after risky batches. For UI, screenshots before and after are the test.
- Always record whether the build and linter pass **before** you touch anything.

## 2. Finding problems (framework-agnostic commands)

Adapt paths and extensions to the project.

```bash
# largest files (candidates to split)
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.py" -o -name "*.java" -o -name "*.dart" -o -name "*.vue" -o -name "*.svelte" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/build/*" \
  -exec wc -l {} + | sort -rn | head -20

# most frequently changed files (hotspots; need extra care and tests)
git log --since="1 year ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20

# who uses a symbol before you move or rename it
grep -rn "SymbolName" --include="*.ts" --include="*.tsx" . | grep -v node_modules
```

Signals that a file needs work:
- Over about 400 lines, or one function over about 60 lines.
- Many unrelated imports (it does several jobs).
- Copy-pasted blocks (same 5+ lines in 3+ places).
- Deep nesting (4+ levels), long parameter lists (5+), boolean flag parameters that switch behavior.
- Business logic mixed into UI code, or UI/IO code mixed into business logic.
- Circular imports.

Write the top findings into `PLAN.md` as a ranked list. Fix the ones that block the user's goal first, not everything you can find.

## 3. Strategies for big changes

Pick one per change and write it in the plan.

**Parallel change (expand, migrate, contract).** Safest default.
1. Expand: add the new function/component/module next to the old one. Both work.
2. Migrate: move callers over a few at a time, verifying after each batch.
3. Contract: when nothing uses the old one, delete it.

**Strangler.** For replacing a whole subsystem: put a thin wrapper in front, route one
feature at a time to the new implementation, retire the old one last.

**Branch by abstraction.** Introduce an interface/adapter that both old and new
implementations satisfy, switch callers to the interface, then swap the implementation behind it.

**Mechanical sweep.** For renames and API changes that touch many files in the same way
(see section 6). Do these in their own batch with no other changes mixed in.

Avoid "big bang" rewrites. If the user asks for one, propose the parallel-change version and explain that it
reaches the same result with a working app at every step.

## 4. Common moves (use the smallest one that works)

| Problem | Move |
|---|---|
| Long function | Extract function: name the extracted part by *what* it does |
| Giant file | Split by responsibility, not by size. Move one cohesive group at a time, re-export from the old path |
| Duplicated code | Extract shared function/component, then replace the copies one by one |
| Flag parameters | Split into two named functions |
| Deep nesting | Early returns / guard clauses |
| Magic numbers/strings | Named constants or config |
| Logic inside UI | Move to plain functions/hooks/services; UI only calls them |
| Global mutable state | Pass dependencies in explicitly, or wrap in one small module |
| God object/class | Extract cohesive groups of fields+methods into new classes, delegate |
| Inconsistent naming | One mechanical rename batch, with a short naming rule in the plan |
| Circular imports | Move shared pieces to a third module both depend on |
| Dead code | Confirm with grep and tests, delete in the cleanup batch |

Re-export trick: when moving a file, leave the old path exporting from the new one. This lets you migrate imports gradually.
Remove the re-export in cleanup.

## 5. Ordering rules

- Move from the leaves inward: modules with no dependents first, shared core last.
- Change one layer at a time: data/types, then logic, then UI.
- Rename and move in separate batches from logic changes.
- Never refactor a hotspot file without tests around it.
- Upgrade dependencies/frameworks in their own batches, separate from restructuring.

## 6. Large mechanical changes

For the same edit across many files:
1. Write the exact before/after pattern in `PLAN.md` with 2 examples.
2. Prefer a real tool: the language's refactoring/rename tool, `sed`/`perl` for simple text, a codemod tool
   (jscodeshift, ts-morph, libcst, comby) for syntax-aware edits. Use the tool that is already available.
3. Run it on 2 or 3 files, review the diff, then run on the rest in groups.
4. Run build/tests after each group. Review a sample of the diff by eye; do not trust it blindly.

## 7. Rollback

- If the project uses git, commit after each verified batch (or ask the user to). Message format:
  `refactor(<area>): <what changed>`. A bad batch can then be reverted alone.
- If there is no git and you cannot create commits, copy the files you are about to change into a
  `.backup/` folder before the batch, and mention it in `PLAN.md`.
- If a batch fails and you cannot fix it in two attempts, revert it, note why in `PLAN.md`, and ask the user.
