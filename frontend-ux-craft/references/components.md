# Component design

Good components are small contracts: they decide what varies, hide what shouldn't, carry their own
accessibility, and behave predictably in every state. Consistency across a product is mostly
consistency of these contracts.

## Contents
1. Before building: inventory first
2. The state checklist
3. API design (props, slots, composition)
4. Core components: decisions worth making once
5. Feedback: which pattern for which moment
6. Loading, empty, error: three states that make or break trust
7. Destructive actions
8. Icons, shape, elevation, motion
9. Content design inside components
10. Density and theming hooks
11. Component review checklist

---

## 1. Before building: inventory first

1. Search the project for an existing component (and its story/usage). Reuse or extend before creating.
2. If a library is in play (Material, PrimeVue, Radix-based kit), wrap or theme it; don't fork a parallel one.
3. If genuinely new, check `DESIGN.md` §6, name it by **what it is**, not where it's used (`DataTable`, not `DashboardTable`; `Field`, not `LoginInput`).
4. Update the inventory when you add something. An undocumented component is a future duplicate.

## 2. The state checklist

A component isn't done until each applicable state has been designed, not just the happy path.

| State | Notes |
|---|---|
| Default / rest | |
| Hover | Pointer only; never the only signal (touch has none). Don't reduce contrast. |
| **Focus-visible** | Keyboard focus ring that's visible on all surfaces. |
| Active / pressed | Tactile feedback: 1-2px shift, slight darken; ≤100ms. |
| Disabled | Use sparingly. Prefer explaining *why*; use `aria-disabled` + keep focusable if the reason matters. |
| Loading / busy | Preserve size to avoid layout shift; keep label; `aria-busy`. |
| Selected / current / checked | Not color alone (check mark, weight, indicator bar). |
| Invalid / error | Text + icon + `aria-invalid`; keeps input. |
| Read-only | Different from disabled: still readable, copyable, focusable. |
| Empty | Teach the next action. |
| Overflowing | Long text, many items, tiny container: truncate, wrap, or scroll *deliberately*. |
| Right-to-left / long translations | Logical properties; allow ~40% text growth. |

Test each with **real-world content**: 1-character and 60-character names, "Ólafur Þórðarson", "李小龍", numbers like `1,234,567.89`, dates in other locales, zero / one / many items.

## 3. API design (props, slots, composition)

- **Small surface, strong defaults.** `variant` (a few named values), `size` (2-3), plus native attributes. If you're adding a 9th boolean prop, you probably need composition (slots/children) instead.
- **Composition over configuration:** `<Card><Card.Header/>…</Card>` (React), `<ng-content select="[slot=header]">` (Angular), named `<slot>`s (Vue). Consumers arrange; the component enforces semantics.
- **Pass through native attributes** (`...rest` in React, `v-bind="$attrs"` in Vue, host bindings/attribute inheritance in Angular) and **forward refs** where relevant, so consumers can add `aria-*`, `data-*`, `id`, `onClick` without you predicting them.
- **Accessibility is not optional API.** Required props for things that must be named (`aria-label` on icon-only buttons: make the type system demand it). The component wires `id`/`aria-describedby` for label, hint, and error internally (`useId` in React 18+, `useId()` in Vue 3.5+, generated ids in Angular).
- **Controlled *and* uncontrolled** for form-like widgets (`value/onChange` + `defaultValue`; `v-model`; `ControlValueAccessor` in Angular so it works with Reactive Forms).
- **Semantic HTML underneath.** `<Button>` renders `<button>`; a `as`/`asChild` escape hatch renders a link, but keep the same look and role rules.
- **Style through tokens.** No raw colors, px values, or z-indexes in components. Variants map to roles (`--brand`, `--danger`).
- **No hidden global side effects.** Components don't set body scroll lock, add listeners, or inject styles without cleaning up.
- Emit **events with meaning** (`onSave`, `@confirm`, `(dismissed)`), not raw DOM events wherever a domain event exists.

## 4. Core components: decisions worth making once

**Button**
- Hierarchy: **one primary per view/section**, then secondary (outlined or tonal), then quiet/ghost, plus danger. Two primaries = no primary.
- Label = verb + object ("Save changes", "Invite teammate"). Never "Submit"/"OK"/"Yes".
- Icon + text preferred; icon-only needs an accessible name and a tooltip. Keep icon size proportional to text; align optically.
- Loading: replace the icon (or prepend spinner) without changing width; disable *re-submission*, not focus.
- Links that look like buttons are still links (`<a>`). Buttons that navigate are a bug.

**Text field / Field wrapper** (build **one** `Field` used by every input type)
- Anatomy top→bottom: label, optional hint, control, error. Same order everywhere.
- Width matches expected input (zip code ≠ full-width). Don't stretch everything to 100%.
- Show password toggle (as a button with state), clear button where useful, character counters only when a limit matters.
- Number inputs: prefer `type="text" inputmode="numeric"` for IDs/codes; `type="number"` for true quantities; format on blur, not on each key.

**Select / Combobox** Native `<select>` for ≤ ~15 simple options; combobox with search beyond; always keyboard-complete; no hover-only open.

**Checkbox / Radio / Switch** Whole row is the hit target; group label via fieldset/legend; switch = immediate effect (no Save button), checkbox = staged choice. Never make a switch that needs a separate Save.

**Dialog / Sheet / Popover / Inline**
- Inline expansion first (least disruptive) → popover (small, contextual) → sheet/drawer (secondary task, keeps context) → modal dialog (blocking, a decision is required). Don't use a modal for content that could live on a page.
- Title states the purpose; primary action verb-labelled; destructive style only on truly destructive; footer button order is decided once in `DESIGN.md`.
- Mobile: dialogs become bottom sheets or full-screen pages; keep the primary action reachable by thumb.

**Table / List**
- Left-align text, right-align numbers (tabular figures: `font-variant-numeric: tabular-nums`), consistent decimals; units in header.
- Sticky header for long tables; sortable headers are buttons with `aria-sort`; row click only if the row also contains a real link/button for the same action.
- Selection + bulk actions: a contextual toolbar appears when ≥1 selected, announcing the count.
- Mobile: prioritise 2-3 key fields as a card/list row with the rest in a detail view; don't shrink a 9-column table.
- Pagination or "Load more" over infinite scroll for anything people need to return to.

**Navigation** Current location visibly and semantically marked (`aria-current="page"`); limit top-level to ~5-7 items; breadcrumbs for depth ≥3; labels are nouns people use, not internal module names.

**Tabs** Peers of the same object (Overview / Activity / Settings), not steps in a process, and not more than ~6.

**Badge / Tag / Chip** Status = color + icon/text. Don't turn every metadata field into a colored pill; it becomes noise.

**Avatar** Image with initials fallback on a deterministic color; `alt=""` if the name is adjacent, else the name.

**Toast** See feedback. One at a time, or a small stack; never stack a wall.

## 5. Feedback: which pattern for which moment

| Situation | Pattern | Why |
|---|---|---|
| Field-level problem | Inline error under field | Right place, right time |
| Action succeeded, no follow-up | Subtle toast/inline "Saved" via live region | Confirms without interrupting |
| Action succeeded, reversible | Toast **with Undo** (long enough to use) | Trust; cheaper than confirm dialogs |
| Persistent system state (offline, read-only mode, degraded) | Banner at top of the affected region | Must remain visible |
| Form-level failure | Error summary at top + focus | Screen-reader and scanning friendly |
| Blocking decision | Dialog | Only when a choice is required |
| Long-running job | Progress in place + notification when done (with link) | Don't trap them |
| Optimistic update | Apply immediately, roll back with a clear message on failure | Feels instant |

## 6. Loading, empty, error: three states that make or break trust

**Loading**
- Under ~100ms: show nothing special. 100ms-1s: subtle inline indicator. >1s: skeleton that mirrors the final layout (same heights → no layout shift). >10s: progress + explanation + cancel.
- Show stale data with a subtle "updating" affordance rather than blanking the screen on refetch.
- Reserve space for images and embeds (`aspect-ratio`, width/height) to protect CLS.

**Empty**
- Say *why* it's empty and give the next step: "No invoices yet. Create your first invoice" + a real button. Different copy for "nothing yet", "nothing matches your filters" (offer "Clear filters"), and "you don't have access".
- Don't fill emptiness with a cute illustration and no action.

**Error**
- Say what happened, whether their data is safe, and what to do next, with a retry that works. No stack traces, no "Something went wrong" alone, no blame, no jokes about failure. Log details separately (without secrets/PII).
- Error boundaries per **region** (a broken widget shouldn't blank the page). Offline: detect and say so; queue writes if the domain allows.
- Distinguish 401 (sign in again, preserve their work + return URL) / 403 (you don't have permission + who to ask) / 404 / 5xx / network.

## 7. Destructive actions

Prefer **Undo over "Are you sure?"**: confirmations get reflexively dismissed. Use a confirm dialog only when the action is irreversible or costly, and then:
- Title names the object: "Delete “Q3 invoices”?"; body states consequence in plain words; the destructive button repeats the verb ("Delete invoice"), styled as danger; the safe option is the easy default and initial focus.
- For truly high-stakes actions (delete account/org), require typing the resource name.
- Batch delete: state the count.

## 8. Icons, shape, elevation, motion

- **One icon set, one stroke weight, one size grid** (16/20/24). Mixed sets are the fastest tell of an assembled UI. Align icons to the text baseline/cap-height; tune `gap`.
- Never use emoji as UI icons or bullet decoration (renders differently per OS, screen readers announce them).
- **Radius follows role** (control < surface < overlay), and nested radii shrink: inner radius = outer radius − padding. Same radius on everything looks like a template.
- **Elevation:** choose one strategy: borders-with-flat, or soft shadows. Overlays (menus, dialogs) are the only things that get strong shadows.
- **Motion answers an action** (opens, expands, confirms, reorders) in 120-250ms with ease-out; exit faster than enter. Keep transforms/opacity only (compositor-friendly). No entrance animation on every card, no hover lift on everything. Respect reduced motion.

## 9. Content design inside components

- Sentence case; plain verbs; front-load the meaningful word; cut filler ("Please", "Successfully", "Are you sure you want to").
- Same thing, same word, everywhere ("Delete" not "Remove" here and "Trash" there). Put the glossary in `DESIGN.md`.
- Numbers, dates, currency formatted with `Intl.*` for the person's locale, not string concatenation. Relative time has an absolute time on hover/focus/`<time datetime>`.
- Pluralization via ICU/i18n library; never `${n} item(s)`.
- Truncate with intent: keep the distinguishing end of file names (`report-final-v3.pdf`, truncate the *middle*), expose full text on focus/hover and to AT.

## 10. Density and theming hooks

- Provide `comfortable` and `compact` density by scaling spacing tokens, not by making every component reimplement it (`data-density="compact"` on a container that overrides `--space-*` and control heights). Compact for dense expert tools; comfortable is default; never go below the 24px target floor.
- Expose only *tokens* for customization. If consumers need `!important` or deep selectors to fix your component, the API is missing a hook.

## 11. Component review checklist

- [ ] Reused/extended an existing component where possible
- [ ] Native element underneath; role/keyboard model complete
- [ ] All states designed (see §2), including focus-visible, loading, error, empty, overflow
- [ ] Name/label/description wiring internal, not left to the consumer
- [ ] Tokens only: no raw colors/px/z-index
- [ ] Works at 320px, at 200% zoom, in dark mode, in forced-colors, with reduced motion
- [ ] Realistic long/short/international content tested
- [ ] Copy is sentence case, verb-led, consistent with the glossary
- [ ] Added to the inventory
