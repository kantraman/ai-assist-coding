# Changing the design of an existing project

Redesigning a live codebase is a different job from designing a blank page. There are real people who
have learned the current interface, real code with hidden dependencies (tests, analytics, CSS hooks,
third-party embeds), and real risk. The skill is in changing **a lot of appearance and structure while
changing very little behavior**, in steps small enough to review, ship, and roll back.

## Contents
1. Golden rules
2. Decide the mandate
3. Discover and baseline
4. Diagnose before prescribing
5. Choose the migration strategy
6. Token-first migration, phase by phase
7. Mapping the legacy palette and values to roles
8. Restructuring a screen (layout and placement changes)
9. Coexistence: old and new side by side
10. Stack-specific notes
11. Keeping behavior, tests, and hooks safe
12. Respecting people who already know the product
13. Prioritization
14. Verification and definition of done
15. What to report back
16. Pitfalls

---

## 1. Golden rules

1. **Read before you touch.** Run the app, click through it, read the styling approach and component structure. Never restyle from a description alone.
2. **Behavior is a contract; appearance isn't.** Don't change routes, form field names, API calls, validation logic, or business rules while restyling. If a UX fix needs a behavior change, isolate and flag it.
3. **Tokens first, then looks.** Make the current design *expressible* as tokens with no visual change; then the redesign becomes changing token values plus structural fixes. This is the safest path and it produces consistency as a side effect.
4. **Small, reversible steps.** One phase or one area per change, each shippable, each with a before/after. Avoid the big-bang rewrite branch that never merges.
5. **Extend the existing system.** If tokens, a component library, or a `DESIGN.md` already exist, evolve them; don't create a parallel one. If two systems already coexist, pick the winner and migrate toward it.
6. **Fix the floor while you're there.** A redesign that keeps a keyboard trap or an XSS sink has failed. Accessibility blockers and security holes found during the audit are in scope even for "just a reskin". Report them; fix the ones touching code you're changing.
7. **Preserve what works.** Muscle memory is an asset. Change placement, navigation, and naming only with a reason you can state in one sentence (see §12).
8. **Don't ship the autopilot look.** A redesign is the moment projects slide into generic gradient-and-rounded-card SaaS. Run the point-of-view procedure in `humanizing.md` §2, anchored to the product's actual audience and any existing brand equity.

## 2. Decide the mandate

Requests like "redesign this" or "make it modern" hide very different scopes. Identify which one applies, state it in a line, and confirm only if the wrong guess would waste real effort.

| Mandate | What changes | What must stay | Typical approach |
|---|---|---|---|
| **A. Targeted fix** ("this form is confusing", "the table is unusable on mobile") | One area | Everything else | Diagnose that area, apply contract rules locally, use existing tokens |
| **B. Refresh / reskin** ("new brand", "make it look better", dark mode) | Colors, type, radius, spacing, elevation, icon style, copy tone | Layout, flows, IA | Token-first migration (§6); minimal structural edits |
| **C. Restructure** ("users can't find things", "dashboard is cluttered") | Layout, navigation, placement, flows, information hierarchy | Data, permissions, backend behavior | Screen-by-screen redesign (§8) on top of tokens; preserve URLs |
| **D. Rebuild / migrate** (new framework or component library) | Implementation | Look and behavior (or deliberately, both) | Strangler pattern (§5, §9), parity checks, route-by-route cutover |

Default when unspecified: **B with A-style fixes for glaring usability/accessibility issues.** Escalate to C only when the problem statement (§4) demands it.

If the person gives a Figma link, screenshots, brand guidelines, or a reference site, treat those as constraints and read them before deciding.

## 3. Discover and baseline

Spend a few minutes measuring so the redesign is judged against numbers, not vibes.

1. **Stack and conventions:** `package.json`, framework, routing, styling approach (Tailwind, Sass, CSS Modules, CSS-in-JS, Bootstrap, Material), component library and version, lint/format config, test setup, build tool.
2. **Run the audit script** from the project root and save the output as the baseline:
   `python scripts/audit_project.py <project-root> > audit-before.txt`
   It reports distinct colors/font sizes/radii/shadows/z-indexes/breakpoints, whether a token layer exists, `!important` and inline-style counts, a11y smells (outline removal, click-on-div, img without alt, disabled zoom), and security smells (HTML sinks, sanitizer bypasses, tokens in storage, public-env secrets). The numbers are leads, not verdicts; verify the important ones by reading the code.
3. **See it running.** Screenshot key screens at 375 / 768 / 1440 in light (and dark if it exists). Note which screens matter most (traffic, revenue, support tickets, or what the person names).
4. **Inventory the components:** what's reused vs. re-implemented (five different button styles is a finding). Where does the shell live (layout, nav, header)?
5. **Find the hooks that must not break:** CSS class names or IDs used by JS, tests (`data-testid`, selectors), analytics, GTM, print styles, email templates, embedded widgets, third-party overrides.
6. **Existing brand and content:** logo, colors in marketing material, tone of existing copy, legal/regulatory constraints (e.g. required disclosures, accessibility statements).
7. **Evidence of pain, if any exists:** support tickets, analytics drop-offs, session notes, complaints. If none is available, say the diagnosis rests on heuristics and reading the product.

If a step can't be done (no browser, no dev server), say so and proceed from code, listing what remains unverified.

## 4. Diagnose before prescribing

Write a short **problem statement** with three parts: *who struggles, at what moment, and why*. Then separate:

- **Doesn't work** (blocks or slows people): keyboard traps, invisible focus, unreadable contrast, broken mobile layouts, missing error states, confusing hierarchy, unclear primary action, inconsistent placement, security exposure.
- **Doesn't cohere** (inconsistent): five blues, four radii, three button styles, dialogs with buttons in different orders.
- **Feels dated / off-brand** (aesthetic): type, spacing, imagery, icon style.

Fix in that order. Most projects asking for a "redesign" are mainly in the second bucket, which tokens plus component consolidation solve more cheaply and more durably than new visuals.

A quick heuristic pass per key screen (10 minutes each): Where is the primary action? What's the first thing the eye lands on? What happens with empty/error/loading/long content? Can I do it by keyboard? What breaks at 320px? Where does this screen violate the placement contract (create one if none exists; see `layout-and-responsive.md` §4)?

## 5. Choose the migration strategy

| Strategy | Use when | Trade-offs |
|---|---|---|
| **Token-first, in place** (recommended default) | Reskin/refresh; one styling system | Safest; visible improvement arrives at the "swap values" phase; needs discipline replacing raw values |
| **Scoped theme switch** (`[data-ui="v2"]` or feature flag) | Big visual change; need A/B, staged rollout, or opt-in preview | Temporary CSS duplication; must delete v1 afterward |
| **Strangler by route/section** | Framework or library migration; huge apps | Two UIs coexist; shared shell and tokens are essential to avoid a Frankenstein feel |
| **Big-bang rewrite** | Almost never | High risk, long-lived branch, regressions, stalls |

Tell the person which you chose and why in one or two sentences.

## 6. Token-first migration, phase by phase

Each phase should be a reviewable, shippable change. Verify with the audit numbers and screenshots.

**Phase 0: Safety net**
- Make sure the project builds and its tests pass *before* you start; note pre-existing failures.
- Capture screenshots (or set up a visual-regression baseline: Playwright/Chromatic/Percy/Loki) for key screens.
- Run an a11y scan (axe) and record the count. Add lint rules that don't yet fail the build.

**Phase 1: Introduce tokens with zero visual change**
- Add the token file (start from `assets/tokens.css` structure). Populate role tokens with the **current** values: the existing primary color becomes `--brand`, the existing body text color `--text`, and so on.
- Bridge existing variable systems to the new roles with aliases (§7), rather than rewriting everything at once.
- Expected result: identical screenshots, and a token layer exists.

**Phase 2: Replace raw values with tokens**
- Work from the audit lists: each distinct hex/px value maps to a role (§7). Replace in mechanical passes by category (colors → spacing → radius → shadow → z-index → type), one PR per category or area.
- Collapse near-duplicates deliberately (`#3b82f6`, `#3b83f7`, `#3a80f5` → `--brand`); this is where small visual changes occur. Note them.
- Delete duplicated component styles as you go by pointing them at shared components.
- Expected result: audit's "distinct values" counts fall sharply; screenshots nearly identical.

**Phase 3: Swap the values (the reskin)**
- Now change the token values to the new design: hues derived from the subject, tinted neutrals, type roles, radius by role, elevation strategy, motion. Verify contrast with `scripts/check_tokens.py`; add the dark theme if wanted (`light-dark()` tokens).
- Because components read roles, the whole product updates at once. Review screens for problems tokens can't fix (fixed-width text, icons that were raster images, hard-coded logo colors, brand imagery).
- Expected result: new look everywhere, same structure.

**Phase 4: Consolidate and upgrade shared components**
- Buttons, fields, dialogs, tables, alerts, tabs, nav: one implementation each, all states, accessible by construction (`components.md`). Replace the duplicates across the app.
- Introduce/repair `Field` (label, hint, error wiring), focus rings, live-region toasts, dialog focus management.

**Phase 5: Shell and navigation**
- Apply the placement contract to the app shell (title, primary action location, nav pattern per breakpoint, help/support, account menu). Fix skip link, landmarks, route-change focus/title.

**Phase 6: Screens, by priority**
- Top screens first (§13). Use the screen recipe in §8. One screen or flow per change.

**Phase 7: Clean-up**
- Delete dead CSS/components, the v1 theme, temporary aliases, and unused libraries. Remove `!important` and deep selectors that existed to fight the old system.

**Phase 8: Lock it in**
- Add guardrails so drift can't return: stylelint rules (`color-no-hex` with token allowlist, `declaration-property-value-disallowed-list` for raw z-index, `selector-max-specificity`), ESLint a11y plugin as errors, a CI step running the audit script and failing if raw-color counts increase, axe in tests, and a short `DESIGN.md` with the decisions.

## 7. Mapping the legacy palette and values to roles

**Procedure**
1. List distinct colors from the audit (or `rg -oI '#[0-9a-fA-F]{3,8}\b' -g '*.{css,scss,vue,tsx,html}' | sort | uniq -c | sort -rn`).
2. **Cluster** by function and proximity (which are "the blue"? which grays are text vs. borders vs. backgrounds?). Look at where each is used (selector context) before deciding.
3. **Assign roles**: `--bg`, `--surface`, `--surface-sunken`, `--border`, `--border-strong`, `--text`, `--text-muted`, `--text-subtle`, `--brand`, `--on-brand`, `--brand-text`, `--brand-subtle`, `--danger*`, `--success*`, `--warning*`, `--info*`.
4. **Resolve conflicts**: same color used for two meanings gets split into two roles; near-identical values are merged.
5. Do the same for spacing (snap to the 4px scale), type sizes (snap to a scale), radii (control/surface/overlay), shadows (one or two), z-index (the scale in tokens), and breakpoints (2-4 content-driven values).
6. Keep a short **mapping table** (old value → role → notes) in the PR or `DESIGN.md`; it's your migration log and your reviewer's guide.

**Alias bridge**: keep old names working while callers migrate, then delete the aliases.
```css
:root {
  /* new role tokens (source of truth) */
  --brand: light-dark(oklch(50% .085 200), oklch(72% .12 200));

  /* legacy names → new roles (delete once no callers remain) */
  --primary-color: var(--brand);
  --main-blue: var(--brand);
  --color-text: var(--text);
}
```
- **Sass variables:** define `$primary: var(--brand);` so existing SCSS keeps compiling; migrate call sites over time. Sass color functions (`darken($primary, 10%)`) don't work on `var()`: replace with `color-mix(in oklch, var(--brand), black 12%)`.
- **Tailwind:** point `theme.extend.colors` (v3) or `@theme` (v4) at role variables and stop using palette utilities in components (`bg-blue-500` → `bg-brand`). Codemod or find/replace by mapping table; run Prettier's Tailwind plugin to reorder.
- **CSS-in-JS (styled-components/Emotion):** move the theme object's values to `var(--role)` strings; components stay unchanged.
- **Component libraries (Bootstrap, Material, PrimeVue, Vuetify, Ant):** use their theming API/variables to bind to your roles; don't override with `!important` or deep selectors.
- **Icons/images with baked colors:** convert SVGs to `currentColor`; supply dark-mode variants for raster art.

## 8. Restructuring a screen (layout and placement changes)

Use this recipe for mandate C, or for any screen with real structural problems.

1. **Capture what the screen does**: its jobs, data shown, actions, states, permissions, and the URL/route. List everything that must still be possible afterward.
2. **List the problems** from §4 (blocking / incoherent / dated) for this screen only.
3. **Apply the placement contract**: title, primary action, filters, bulk actions, form actions, feedback locations. If no contract exists, define it now in `DESIGN.md` from the most common current pattern (or the best one already present) so the redesign converges rather than adds another variant.
4. **Wireframe before/after** in ASCII (mobile first, then wide). Show the person if the change is significant.
5. **Design all states**: loading, empty, error, no-permission, long content, many items.
6. **Rebuild with existing data flow**: keep props, stores, API calls, and validation; swap only the presentational layer and structure. Preserve `id`s, `name`s, `data-testid`s, and the URL.
7. **Check responsive behavior** with the transformations table in `layout-and-responsive.md` §6.
8. **Verify**: keyboard path, screen-reader smoke test if possible, 320px, dark mode, tests pass, visual diff reviewed.

Common structural upgrades that pay off: one obvious primary action; filters directly above the list with an applied-count on mobile; forms in a single column with labels above; tables that become cards on mobile; dashboards that lead with the number people came for; navigation that shows the current location; dialogs that become bottom sheets on phones; destructive actions separated from safe ones; undo instead of confirm.

## 9. Coexistence: old and new side by side

Use only when needed for staged rollout or migration; plan its removal from day one.

- **Scope with an attribute or class** on a layout root: `<body data-ui="v2">`. Put v2 tokens under `[data-ui="v2"] { ... }`. Flip it by user flag, environment, or route.
- **Layer the CSS** so specificity is predictable: `@layer reset, legacy, tokens, components, utilities;` legacy styles go in the `legacy` layer (lower priority), new styles win without `!important`.
- **Share the shell and tokens** across old and new screens so they don't feel like two products; migrate the shell early.
- **Route-level cutover:** new screens replace old at the same URL; redirect if URLs must change.
- **Feature flags:** wrap at the highest level (layout or route), not sprinkled through components.
- **Track and delete:** list what's temporary (aliases, v1 styles, flag checks) in the PR description and remove it in Phase 7.

## 10. Stack-specific notes

**React / Next.js**
- CSS Modules/Tailwind/styled-components all work with tokens; keep component APIs stable while swapping internals. For codemods use `jscodeshift` or ast-grep; for simple string mapping, `rg` + `sd`/`sed` with a reviewed mapping table.
- Replace copy-pasted UI-kit defaults (e.g. shadcn) by editing their token variables and component variants, not by overriding with page-level classes.

**Angular**
- Mind **view encapsulation**: styles are scoped per component; global tokens via `styles.scss`/`:root` reach everywhere. Replace `::ng-deep` hacks by using the library's theming/density APIs or wrapping the component.
- Angular Material: migrate to the current theming API (Material 3 system tokens as CSS variables) and bridge your roles to them; don't hand-edit component CSS.
- Keep `[class.x]`/`ngClass` hooks that logic depends on; change what the class *does*, not its name, unless you update all references.

**Vue / Nuxt**
- Scoped styles are safe to refactor per component; replace `/deep/`/`::v-deep` with `:deep()` sparingly or better, tokens. Keep `<slot>` contracts stable.
- Vuetify/PrimeVue: theme via their token/preset APIs.

**Inertia (Laravel)**
- Layouts are the leverage point: change the persistent layout (nav, header, toast/live region host) once and every page inherits. Blade root view holds `<head>`, theme attribute, and fonts; set `data-theme` server-side from a cookie to avoid a flash.
- Don't change props shapes or route names as part of a visual change; controllers, policies, and validation stay untouched. If you must trim props for security (over-sharing models), do it as a separate, called-out change.
- Blade/Livewire legacy pages coexisting with Inertia pages: share the same CSS entry and tokens.

**Bootstrap / jQuery-era projects**
- Keep Bootstrap's JS behaviors if they work; re-theme via its CSS variables (Bootstrap 5.3+) or Sass variables, then progressively replace components. Watch for outdated modals/carousels that fail accessibility; replace those first.

**Design handoff (Figma/brand PDFs)**
- Extract tokens (colors, type, spacing, radii) into the token file first, then implement components. Flag anything in the mock that fails contrast or hit-target rules and propose an adjusted value rather than silently shipping it.

## 11. Keeping behavior, tests, and hooks safe

- Grep for every class/ID you plan to rename or remove; check JS, tests, analytics selectors, GTM triggers, CSS in emails/print, and third-party overrides.
- Preserve `data-testid`, `name`, `id`, `aria-*` contracts used by tests and assistive tech (and update tests intentionally when the accessible name improves).
- Keep URLs, query params, and anchors stable (SEO, bookmarks, support docs). If they must change, add redirects.
- Don't touch API contracts, validation rules, or auth flows for a visual change.
- After each phase: build, type-check, lint, run unit/E2E tests, review the visual diff. Investigate every unexplained pixel shift.
- Watch for **layout-dependent logic** (JS measuring elements, virtual lists with fixed row heights, sticky offsets, hard-coded header heights); a design change can break these silently.

## 12. Respecting people who already know the product

- **Keep what people rely on:** primary navigation labels and order, location of the main action, keyboard shortcuts, terminology. Change with a reason: "the primary action moved because it was invisible at 320px", not "it looks nicer".
- **Change in layers:** appearance first (low disruption), then structure, then flows. Don't do all three in one release for a heavily used tool.
- **Give a way through:** a short "What's new" note or first-run tip for significant changes; an opt-in preview or toggle for major redesigns of expert tools; a feedback route.
- **Expert tools:** density and speed beat airiness. If the redesign makes tables 30% less dense, offer a compact mode.
- **Measure if possible:** task completion, error rates, support volume, before vs. after.

## 13. Prioritization

Order work by **harm removed and reach**, not by what's most visible:

1. Accessibility blockers and security exposures on any code you touch (a11y: keyboard traps, missing labels, unreadable contrast; security: HTML sinks, secrets in the bundle, tokens in storage)
2. Shared foundations that touch everything: tokens, shell/nav, Button, Field, Dialog, Table, focus and live regions
3. Highest-traffic / highest-value flows (checkout, sign-in, core workflow, dashboard)
4. Mobile breakage
5. Long-tail screens and polish (illustrations, motion, empty states)

For each candidate, estimate **impact × reach ÷ effort**; do the high scorers first and say what you're deferring.

## 14. Verification and definition of done

- [ ] Build, type-check, lint, and tests pass (or pre-existing failures are documented)
- [ ] Re-run `audit_project.py`: raw color/px/z-index counts down; token usage up; a11y and security findings down or explained
- [ ] `check_tokens.py` passes in light and dark
- [ ] Screenshots before/after at 375 / 768 / 1440 reviewed; unexpected diffs explained
- [ ] Keyboard path works on changed screens; focus visible; dialogs and route changes manage focus
- [ ] All states (loading, empty, error, long content) exist for changed components
- [ ] No behavior change unless explicitly called out (routes, names, ids, API, validation)
- [ ] Temporary code (aliases, v1 styles, flags) removed or tracked with an owner
- [ ] `DESIGN.md` reflects the decisions; guardrails (lint/CI) prevent drift
- [ ] Anything not verified (no screen reader, no real device) is listed plainly

## 15. What to report back

Keep it short and decision-focused:

1. **Scope and mandate** you took (A/B/C/D) and the strategy (§5), with the reasoning in a sentence.
2. **Before/after numbers** from the audit (distinct colors, raw values, `!important`, findings fixed).
3. **What changed visually and structurally**, and what deliberately *didn't* (behavior, URLs, hooks).
4. **Decisions worth challenging** (placement changes, removed patterns, merged colors).
5. **Found but not fixed** (with severity), especially security and accessibility items outside the touched code.
6. **Next steps** in priority order, and any temporary scaffolding still to remove.

## 16. Pitfalls

- Restyling components one by one with raw values (creates a *third* inconsistent look)
- Big-bang branch that drifts from main until it can't merge
- Changing behavior "while we're here" and losing the ability to bisect regressions
- Swapping in a trendy kit and leaving its defaults untouched, so the product looks like every other one
- Hiding old problems under new paint: contrast failures, missing focus states, unlabeled icon buttons
- Renaming classes that tests, analytics, or third-party scripts depend on
- Dark mode by inversion, or a second palette maintained by hand instead of by tokens
- Forgetting the surfaces outside the app: emails, PDFs, print styles, error pages, login screens, embedded widgets
- Leaving temporary aliases and v1 CSS in place until they're permanent
- Moving things people rely on with no explanation
