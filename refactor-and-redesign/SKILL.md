---
name: refactor-and-redesign
description: Plan and execute large-scale code refactors and UI redesigns (layout, components, design tokens, color themes, dark mode) safely, in small verified batches. Use this skill whenever the user wants to restructure, rewrite, migrate, modernize, split up, or clean up a codebase or large files, pay down tech debt, change architecture, reskin or redesign a UI, change a color palette or theme, add dark mode, or build a design system or design tokens, even if they never say "refactor" or "redesign". Works with any language or UI framework.
---

# Refactor and Redesign

Large changes fail when they are done in one big pass. This skill makes the work
small, ordered, and checkable. Follow the phases in order. Do not skip a phase.

## Core rules (read these first, they apply to every phase)

1. **Never change behavior and structure in the same step.** A refactor keeps
   behavior identical. A redesign changes looks but not logic. If you must do both,
   do them in separate batches. Reason: when something breaks, you need to know which change caused it.
2. **Work in batches.** One batch = one small, reviewable change (about 1 to 8 files).
   After each batch, verify, then record progress. Never start the next batch on a broken state.
3. **Write progress to a file.** Keep `PLAN.md` in the project root (template in
   `references/templates.md`). Update it after every batch. Your memory of earlier
   steps will fade in a long task; the file will not. At the start of every session, read `PLAN.md` first.
4. **Measure before you change.** Count things (files, lines, hardcoded colors,
   duplicated components) so you can prove progress at the end.
5. **Ask at most 3 questions, then proceed with stated defaults.** Do not stall the user.
6. **Do not delete or rewrite what you have not read.** Read a file fully before editing it.
7. **Keep the old path working until the new one is proven** (see "parallel change"
   in `references/refactor-playbook.md`). Remove old code only in a final cleanup batch.

## Phase 0: Scope (ask, then lock)

Decide which of these apply: `refactor` (structure/code quality), `redesign`
(layout, components, visual style), `theme` (colors, dark mode, tokens). Often it is more than one.

Ask only what you cannot find out by looking at the project. Useful questions:
- What is the goal in one sentence, and what must NOT change (public APIs, routes, URLs, data formats)?
- Is there a test suite or a way to run the app? What is the command?
- For redesign/theme: is there a reference (brand colors, screenshot, site, mood words)?

If the user does not answer, assume: keep all public behavior, keep the existing
framework, minimal new dependencies. State these assumptions in `PLAN.md`.

**Gate:** write the goal, non-goals, and assumptions at the top of `PLAN.md`.

## Phase 1: Map (read-only, change nothing)

Build an inventory. If you can run commands, run them. If you cannot, ask the user to run them and paste results.

1. List the project structure (top 2 levels) and identify the framework, language, build tool, and test command.
2. Find the biggest files and the most duplicated code (see playbook for commands).
3. For UI work, run `python scripts/find_hardcoded_colors.py <project_dir>` to count every hardcoded color.
   Also list: shared components, style files, and where fonts/spacing are defined.
4. Find the baseline: run the existing tests/build/lint and record whether they pass **before** any change.
   If there are no tests, say so in `PLAN.md` and plan to add a few characterization tests first (see playbook).

**Gate:** record the findings and the baseline numbers in `PLAN.md` under "Inventory".

## Phase 2: Plan

Break the work into ordered batches and write them in `PLAN.md`. Use this order, because later steps depend on earlier ones:

1. Safety net (tests, snapshots, or a manual checklist) if the baseline is weak.
2. Foundations: design tokens / theme file, shared utilities, folder structure.
3. Leaf pieces: small components, pure functions, low-dependency modules.
4. Composed pieces: layouts, pages, services that use the leaf pieces.
5. Cleanup: remove old code, dead styles, unused files; update docs.

Each batch in the plan needs: a name, the files touched, the expected outcome, and how to verify it.
Prefer many small batches over a few large ones.

**Gate:** show the plan to the user as a short numbered list and ask for a go-ahead or edits.
If the user says "just do it", proceed.

## Phase 3: Execute (repeat for each batch)

For every batch, in this exact order:

1. Re-read `PLAN.md`, find the next unchecked batch.
2. Read the files in that batch fully.
3. Make the change. Keep the diff focused on this batch only.
4. Verify: run tests/build/lint, or for UI also check the visual checklist in
   `references/ui-redesign-and-theming.md`. If you cannot run anything, tell the user exactly what to run or look at.
5. If verification fails: fix it, or undo the batch. Do not move on.
6. Tick the batch in `PLAN.md` and add a one-line note of what changed.
7. Reply with the status block below.

Status block (keep replies short and consistent):

```
Batch N done: <name>
Changed: <files>
Verified: <how, and the result>
Next: <next batch>
```

## Phase 4: Finish

1. Run the full test/build/lint again and compare with the Phase 1 baseline.
2. Repeat the Phase 1 counts (file sizes, hardcoded colors, etc.) and report before/after.
3. Remove temporary scaffolding (old paths, compatibility shims, unused files).
4. Write a short summary: what changed, what was intentionally left alone, any follow-ups.

## Which reference to read

- Any structural/code change: read `references/refactor-playbook.md`.
- Any visual/layout/color change: read `references/ui-redesign-and-theming.md`.
- Unsure how to format `PLAN.md` or a theme spec: read `references/templates.md`.

Read only the files you need. For a pure refactor, skip the UI reference.

## Scripts

- `scripts/find_hardcoded_colors.py <dir>`: counts hex/rgb/hsl color literals per file. Use it before and after theming work.
- `scripts/contrast.py <fg> <bg>`: WCAG contrast ratio and pass/fail. Use it for every text/background pair you choose. Do not estimate contrast by eye or by mental math.

## When you are blocked

If a step is ambiguous, risky, or would break a public contract, stop and ask one specific question
with a recommended default. Do not guess silently on anything the user said must not change.
