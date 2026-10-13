# Templates

Copy these and fill them in. Keep the structure; it helps you and the user find things quickly.

## PLAN.md

```markdown
# Plan: <short title>

## Goal
<one sentence>

## Non-goals / must not change
- <public API, routes, data formats, behavior to preserve>

## Assumptions
- <anything the user did not confirm>

## Inventory (Phase 1)
- Stack: <language, framework, build tool>
- Test/build command: `<command>`  | Baseline: <pass/fail, counts>
- Biggest files: <file (lines)>, ...
- Hardcoded colors: <N in M files>
- Other findings: <duplication, hotspots, circular imports>

## Direction (redesign/theme only)
<one sentence describing the visual direction>

## Batches
- [ ] 1. <name> | files: <list> | verify: <how>
- [ ] 2. ...
- [ ] 3. ...

## Log
- Batch 1: <what changed, result of verification>

## Open questions
- <question, with the default you will use if unanswered>

## Final report (Phase 4)
- Before/after numbers:
- Left alone on purpose:
- Follow-ups:
```

## Theme spec (write this before touching code)

```markdown
# Theme: <name>
Direction: <one sentence>

## Primitives
primary-50 ... primary-900: <hex values>
neutral-50 ... neutral-900: <hex values>
success / warning / danger / info: <hex values>

## Semantic tokens        | light      | dark
color-bg                  | <hex>      | <hex>
color-surface             | <hex>      | <hex>
color-surface-raised      | <hex>      | <hex>
color-text                | <hex>      | <hex>
color-text-muted          | <hex>      | <hex>
color-border              | <hex>      | <hex>
color-primary             | <hex>      | <hex>
color-on-primary          | <hex>      | <hex>
color-danger              | <hex>      | <hex>
color-focus-ring          | <hex>      | <hex>

## Contrast results (from scripts/contrast.py)
text on bg: <ratio> PASS | muted on bg: <ratio> PASS | on-primary on primary: <ratio> PASS
```

## Example token file (web, CSS custom properties)

```css
:root {
  /* primitives */
  --blue-500: #3b6fd4;
  --gray-50: #f7f8fa;
  --gray-900: #14171f;

  /* semantic (light) */
  --color-bg: var(--gray-50);
  --color-text: var(--gray-900);
  --color-primary: var(--blue-500);

  /* scales */
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px;  --space-4: 16px;  --space-6: 24px;
  --radius-sm: 4px;  --radius-md: 8px;  --radius-lg: 16px;
  --font-body: system-ui, sans-serif;
}

:root[data-theme="dark"] {
  --color-bg: #0f1219;
  --color-text: #e8eaf0;
  --color-primary: #7a9cf0;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --color-bg: #0f1219;
    --color-text: #e8eaf0;
    --color-primary: #7a9cf0;
  }
}
```

Components then use only `var(--color-*)`, `var(--space-*)`, and so on.
In other frameworks, create the same names in that framework's theme system (see the mapping table in `ui-redesign-and-theming.md`).

## Batch reply (use after every batch)

```
Batch N done: <name>
Changed: <files>
Verified: <how, and the result>
Next: <next batch>
```
