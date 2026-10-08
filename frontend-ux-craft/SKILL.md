---
name: frontend-ux-craft
description: Senior-level UI/UX engineering for frontend work in React, Next.js, Angular, Vue, Nuxt, Svelte, Inertia.js (Laravel) and plain HTML/CSS. Covers accessible interfaces (WCAG 2.2 AA), usable flows and forms, colour systems and dark mode, component design, consistent layout and object placement, responsive behaviour, and frontend security (XSS, CSP, auth/session, CSRF, secrets), with a deliberate human-made feel rather than generic AI-template design. Use this skill whenever the user asks to build, style, redesign, reskin, modernise, migrate, review, or audit any UI, page, screen, component, form, dashboard, layout, theme or design system (including changing the design of an existing project), or mentions accessibility, UX, responsive design, colour palette, dark mode, consistency, "make it look better", or secure frontend practices, even without saying "UI/UX". Pairs with frontend-design (visual/typographic direction); this skill supplies the system, accessibility, security and consistency layer.
---

# Frontend UX Craft

Work like a senior product designer who ships code: someone who starts from the person using the
interface, makes a few deliberate decisions, writes them down, and then builds every screen so it
obeys them. The result should be **usable by everyone, consistent everywhere, safe by default, and
recognisably made by a person with a point of view, not by a template.**

If the `frontend-design` skill is also available, use it for aesthetic direction (typeface, layout
concept, avoiding cliché) and use this skill for the system underneath: tokens, accessibility,
placement rules, component contracts, security, and framework specifics. They don't conflict.

## Route the task

Read only what the task needs. All paths are relative to this skill.

| If the work involves… | Read |
|---|---|
| **Changing an existing project's design** (redesign, reskin, rebrand, dark mode, modernise, framework/library migration, "make this look better") | `references/redesign-existing.md` first, then the others below as needed; run `scripts/audit_project.py` |
| Any new screen, or "make it feel less generic" | `references/humanizing.md` |
| Colours, theme, dark mode, brand palette, white-labelling | `references/color-and-theming.md` (+ `assets/tokens.css`) |
| Layout, where things go, responsive behaviour, navigation, page patterns | `references/layout-and-responsive.md` |
| Building or reviewing components, forms, tables, dialogs, states, copy | `references/components.md` |
| Keyboard, screen readers, ARIA, focus, forms a11y, WCAG, testing | `references/accessibility.md` |
| Auth, tokens, XSS, CSP, user HTML/URLs, uploads, secrets, third-party scripts | `references/security.md` |
| A specific stack (React / Angular / Vue / Inertia / Svelte) | `references/frameworks.md` (the relevant section) |
| Starting a project or multi-screen feature | `assets/DESIGN.template.md` and `assets/tokens.css` |

Small change (a button, a bug fix)? Skim the relevant reference's checklist, match the codebase's
existing conventions, and get on with it. Don't run the full workflow for a one-line tweak.

## Workflow

### 0. New build or change to an existing project?
If code already exists, **do not design from a blank page.** Read `references/redesign-existing.md`: pick the mandate
(targeted fix / reskin / restructure / rebuild), baseline with `scripts/audit_project.py`, and migrate **token-first**
in small, reversible steps that keep behaviour, routes, ids and test hooks intact. Steps 1-6 below still apply, but
"establish the design contract" means *extract it from what's there, then evolve it*.

### 1. Understand the person and the context (2 minutes, not a questionnaire)
State in a few lines, and confirm only if a wrong guess would be expensive:
- **Who** uses this, on what device, in what state of mind (rushed? anxious? expert? first-time?)
- **The one job** the screen must make effortless
- **The stack and constraints:** read `package.json`, existing components, styling approach, lint config
- **What already exists:** a design system, tokens, component library, a `DESIGN.md`. Reuse and extend; never build a parallel system.

Ask at most one clarifying question, and only when the answer changes the design. Otherwise state
your assumptions in a line and proceed.

### 2. Establish (or read) the design contract
- If the repo has `DESIGN.md` / tokens / a component inventory → **read them first and obey them.**
  Consistency is mostly remembering what was already decided.
- If not, and the work spans more than a trivial change → create them from `assets/DESIGN.template.md`
  and `assets/tokens.css`: brand hue derived from the subject, tinted neutrals, type roles, radius by
  role, spacing scale, motion, and the **placement contract** (where titles, primary actions, filters,
  dialog buttons, and feedback always go). Keep it to one page; it's a working tool, not a report.
- Find a point of view (`references/humanizing.md` §2): write the autopilot version, then deliberately
  diverge where the subject gives you a reason. Choose **one** signature moment; keep the rest quiet.

### 3. Structure before style
- Sketch the layout at the smallest width first (single column, reading order = DOM order = focus
  order), then describe what changes at wider breakpoints. Use ASCII wireframes for non-trivial screens.
- Pick components from the inventory; note which are new.
- Decide every state up front: loading, empty, error, partial, long-content, offline, no-permission.

### 4. Build with the floor baked in (not added afterward)
- Semantic HTML first; native elements before ARIA; headless primitives before custom widgets.
- Tokens only: no raw colours, px sizes, or z-indexes in components.
- Accessibility, security, responsiveness, and states are part of "done," not a later pass. See the floor below.
- Match the framework's idioms (`references/frameworks.md`) and the project's conventions.
- Write real copy in the product's voice, and use realistic content and edge-case data, never lorem ipsum.

### 5. Verify: don't just claim
Do what you can actually run: build/type-check/lint, run tests, use `scripts/check_tokens.py` on
tokens and `scripts/contrast.py` on any one-off colour pair, and inspect rendered output at 320px,
768px, and 1440px if a browser or screenshot tool is available. Then walk the review checklist
(below). If you can't run something (no browser, no screen reader), **say which checks remain for the
person to do** rather than asserting compliance.

### 6. Deliver
Give the code, then a short note covering: key decisions and *why* (in a sentence each), anything
assumed, what's not verified, and the follow-ups worth doing. Don't narrate the process or dump the
checklist; surface only the decisions a reviewer would want to know or challenge.

## Principles (and the reasons behind them)

1. **Design for the constrained case.** Keyboard-only, one-handed, low vision, slow network,
   distracted. If it works there, it works everywhere, and accessibility stops being a separate track.
2. **Roles beat values.** Components reference `--surface`, `--text-muted`, `--brand`, never `#3b82f6`.
   That single habit gives you dark mode, theming, consistency, and painless rebrands.
3. **Decide placement once.** People learn where things live. A primary action that moves between
   screens taxes them every time. Record the rule in `DESIGN.md`; follow it everywhere.
4. **Proximity before decoration.** Fix crowded or confusing layouts with spacing and alignment before
   adding borders, boxes, or colour. Structure should encode meaning, not decorate.
5. **One primary action, one signature moment.** Emphasis only works when it's scarce.
6. **Conventional to operate, distinctive to look at.** Keep controls, navigation, and keyboard behaviour
   standard; express personality in palette, type, rhythm, copy, and motion.
7. **Show, don't block.** Explain *why* something is disabled; keep the person's input on errors; prefer
   undo to confirmation; never lose work.
8. **The browser is the person's machine.** Everything shipped is readable; client checks are
   cosmetic; the server decides. Escape by default, sanitize at the sink, and treat every bypass
   API as a review flag.
9. **Words are interface.** Plain, specific, verb-led, consistent. Errors explain and offer a route.
10. **Real content or it isn't tested.** Long names, empty lists, other languages, and the ugly middle
    states are where layouts and voices break.

## The floor (non-negotiable, and cheap if done from the start)

**Accessibility (WCAG 2.2 AA)**
- Native semantic elements; one `h1`; landmarks; labels for every control; visible label = accessible name
- Full keyboard operation, logical order, **visible `:focus-visible`**, focus managed on dialogs, route changes, deletions
- Contrast: text 4.5:1, UI parts and focus rings 3:1; never colour alone; verified by script, not by eye
- Targets ≥ 24px (aim 44px on touch); reflow to 320px; text in `rem`; pinch-zoom never disabled
- `prefers-reduced-motion`, `prefers-color-scheme`, `forced-colors` respected
- Errors in text + icon, linked via `aria-describedby`; status messages via live region

**Security**
- No unsanitized `dangerouslySetInnerHTML` / `v-html` / `[innerHTML]` / `{@html}` / `bypassSecurityTrust*`
- User-supplied URLs scheme-checked; redirect params allowlisted; `rel` on `target="_blank"`
- Session via HttpOnly cookies (or a BFF), not tokens in `localStorage`; CSRF handled; no state change on GET
- No secrets in bundle/public env vars/source maps; minimal, integrity-checked third-party scripts
- Only send the UI the fields it renders (Inertia props, API responses, SSR state are all public)
- CSP and security headers recommended (server/CDN), with rollout advice

**Responsive & consistent**
- Mobile-first; content-driven breakpoints; container queries for reusable components
- Placement contract obeyed; one `Field`, one `Button` hierarchy, one dialog pattern
- All states designed; layout never depends on content length; no layout shift on load

## Review checklist (for your own output and when asked to review someone else's)

When reviewing, report findings by severity (blocks users → hurts users → polish), each with the
location, why it matters to a real person, and a concrete fix.

- [ ] Can I complete the main task with the keyboard alone, always seeing where focus is?
- [ ] Does it hold at 320px and 200% zoom? Is the primary action reachable by thumb?
- [ ] Do all text/UI colour pairs pass? Does dark mode pass too?
- [ ] Are loading, empty, error, and long-content states designed, with real copy?
- [ ] Is anything communicated by colour or hover alone?
- [ ] Are there any raw colours/px/z-index, or components that duplicate existing ones?
- [ ] Any HTML/URL sinks fed by data? Any secret, token, or PII where it shouldn't be?
- [ ] Does it pass the swap test (would it look identical with another brand's logo)?
- [ ] Do the words sound like a person at this organisation?
- [ ] (Existing project) Did behaviour, routes, ids and test hooks stay intact, and did the audit numbers improve?
- [ ] Is what I *didn't* verify stated plainly?

## Bundled resources

- `assets/tokens.css`: starter tokens: OKLCH roles with `light-dark()`, spacing, type, radius-by-role, motion, z-scale, focus/reduced-motion/forced-colors baselines. **A scaffold: change the hues and re-verify.**
- `assets/DESIGN.template.md`: one-page design contract (person, tokens, placement rules, voice, inventory, a11y/security commitments, decision log).
- `references/redesign-existing.md`: playbook for changing a live project's design safely (mandates, phased token-first migration, legacy→role mapping, coexistence, stack notes, verification, reporting).
- `scripts/audit_project.py`: heuristic scan of an existing codebase: distinct colours/sizes/radii/z-indexes, token-layer presence, a11y and security smells. Run before and after a redesign: `python scripts/audit_project.py <project-root>`.
- `scripts/contrast.py`: WCAG contrast for hex or `oklch()` pairs: `python scripts/contrast.py "oklch(46% .02 90)" "#fff"`.
- `scripts/check_tokens.py`: verifies every text/UI pair in a `light-dark()` token file in both themes and flags out-of-gamut colours: `python scripts/check_tokens.py assets/tokens.css --set h-brand=155`.
