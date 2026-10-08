# DESIGN.md: the UI contract for <Product Name>

> Written once, read before every UI change. If a decision isn't here, make it here first,
> then build. Consistency is mostly remembering what you already decided.

## 1. Who and what
- **Person:** <one sentence: who, on what device, in what state of mind. e.g. "a clinic receptionist, on a shared desktop, phone ringing">
- **Core job:** <the one thing this UI must make effortless>
- **Feeling to leave them with:** <2-3 plain words: "calm, unhurried, sure of themselves">
- **Domain vocabulary to borrow from:** <materials, tools, paperwork, signage of the subject. Source of visual ideas>

## 2. Stack constraints
- Framework: <React | Angular | Vue | Inertia+(Vue/React/Svelte) | ...>
- Styling: <Tailwind v4 / CSS Modules / SCSS / component-lib theme>
- Component base: <headless lib + own styles | Angular Material M3 | existing in-house lib>
- Browsers / devices: <evergreen + iOS Safari 16+ ...>  · i18n / RTL: <yes/no>

## 3. Tokens (source of truth: `<path>/tokens.css`)
| Role | Decision | Why |
|---|---|---|
| Brand hue | <h-brand + rationale from the subject> | |
| Neutral tint | <h-neutral> | |
| Display / body type | <families + roles> | |
| Type scale | <sizes in use> | |
| Radius by role | control <>, surface <>, overlay <> | |
| Elevation strategy | <borders OR shadows, not both> | |
| Density | <comfortable / compact + when each applies> | |
| Motion | <durations, easing, what is allowed to animate> | |

## 4. Placement rules (never re-decide these per screen)
- **Page anatomy:** <e.g. title top-left, primary action top-right, filters in a row beneath>
- **Primary action:** one per view. Desktop: <position>. Mobile: <position, e.g. sticky bottom bar>.
- **Dialog footers:** <cancel left / confirm right | or the reverse. Pick one, forever>. Destructive actions: <styling + confirm pattern>.
- **Forms:** <single column; label above; helper text below label; error below field; group by task>
- **Navigation:** desktop <sidebar/topbar>, tablet <>, mobile <bottom tabs / drawer>. Max depth: <>.
- **Tables:** numbers right-aligned, text left-aligned, row actions <far right | overflow menu>, mobile becomes <cards / priority columns>.
- **Feedback:** inline for field-level, toast for confirmations that need no action, banner for persistent system state, dialog only when a decision is required.

## 5. Voice
- Sentence case everywhere. Verbs on buttons ("Save changes", "Send invoice").
- We say: <words we use> · We never say: <words we avoid, including internal jargon>
- Errors say what happened + what to do. No apologies, no blame, no "Oops".
- Empty states teach the next action.

## 6. Component inventory (reuse before creating)
| Component | Location | Variants | Notes |
|---|---|---|---|
| Button | | primary / secondary / quiet / danger | one primary per view |

## 7. Accessibility + security commitments
- Target: WCAG 2.2 AA. Contrast verified with `scripts/check_tokens.py`.
- Focus ring: <color/style>. Skip link: yes. Route change: focus moves to <h1> + title updates.
- Auth model: <httpOnly cookie session | token via BFF>. CSP mode: <nonce | hash | report-only>.
- Rich text / HTML from users: <not allowed | sanitized with DOMPurify at boundary X>.

## 8. Signature moment
The one place this product is allowed to be memorable: <describe>. Everything else stays quiet.

## 9. Decision log
| Date | Decision | Reason |
|---|---|---|
