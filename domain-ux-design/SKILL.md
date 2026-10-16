---
name: domain-ux-design
description: Design and build accessible, responsive layouts, forms, and UI components that are shaped by the business domain and business logic, feel intuitive, grab attention, and have one memorable signature element that makes the whole experience feel one of a kind. Use this skill whenever the user asks for a page, screen, dashboard, form, checkout, onboarding flow, admin panel, component library, landing page, or any UI/UX work tied to a real business (clinic, bank, school, logistics, restaurant, SaaS, marketplace, government service, etc.), and whenever they mention accessibility, responsiveness, usability, user experience, "unique", "intuitive", "eye-catching", or "user-friendly colours", even if they never say "skill" or "design system". Prefer this over generic UI generation any time business rules, user roles, or workflow states should influence how the interface looks and behaves.
---

# Domain-Driven, Accessible UX Design

The goal is an interface that could only belong to *this* business. It feels
obvious to use, works for everyone, looks good on every screen, and has exactly
one thing people remember.

Three ideas drive everything below:

1. **The domain decides the design.** Vocabulary, users, risks, and rules of the
   business determine layout, colour, form structure, and microcopy. Do not
   start from a template; start from the business.
2. **Business logic is UX.** Every rule (eligibility, limits, approvals, states,
   deadlines, permissions) should be visible, predictable, and explained in the
   interface, not discovered through error messages.
3. **Accessibility and delight are not trade-offs.** Build to WCAG 2.2 AA as a
   floor, then spend boldness in exactly one place.

This skill complements `frontend-design` (aesthetic risk-taking and typography).
If both are available, read it too, and follow its guidance on avoiding
generic AI-looking defaults.

---

## Workflow

Work through these phases in order. Keep the planning phases short (a few lines
each) and show the user the **Design Brief** (Phase 4) before or alongside the
code so they can correct wrong assumptions.

### Phase 1: Understand the domain and the logic

If the request doesn't say, infer a concrete proposal and state it as an
assumption in one line. Only ask a question when a wrong guess would waste the
whole build (e.g. no subject at all).

Capture, in your head or in two or three lines of notes:

| Question | Why it matters |
|---|---|
| **Who uses it?** (roles, age, tech comfort, language, assistive tech) | Sets density, type size, tone, input methods |
| **What state of mind are they in?** (anxious, rushed, relaxed, expert, first-time) | Sets colour temperature, pacing, copy |
| **What is the one primary job?** | Sets hierarchy: one dominant action per screen |
| **What are the core entities and their lifecycle?** (e.g. order: draft, placed, packed, shipped, delivered, returned) | Becomes status components, filters, timelines, navigation |
| **What are the business rules?** (limits, eligibility, required docs, approvals, deadlines, pricing, permissions) | Becomes validation, conditional fields, disabled-with-reason states, hints |
| **What is risky or irreversible?** (payments, deletions, medical data, legal consent) | Sets friction: confirmations, undo, review steps |
| **What device and context?** (phone in sunlight, desktop all day, kiosk, one-handed, offline) | Sets layout, touch targets, contrast margin |
| **What words do users actually use?** | Becomes labels and copy; never expose internal system names |

Translate rules into UI decisions explicitly. Examples:

- "Loan amount must be between X and Y based on income" becomes a slider/stepper
  with live bounds and a plain-language explanation, not a rejected submit.
- "Appointments can't be cancelled within 24 hours" becomes a visible cutoff
  time on the booking and a disabled cancel button that says why.
- "Manager must approve refunds over a limit" becomes an approval state in the
  timeline and a "Requires approval" note before the user submits.

### Phase 2: Find the signature

Every design needs **one** memorable, domain-rooted idea. It is the thing a user
would describe to a friend. Pick one, not three.

Derive it from the domain's own objects, materials, rituals, and language:

- **Signature object**: the interface borrows the shape of a real artefact
  (a prescription label, a boarding pass, a ledger, a seed packet, a ticket
  stub, a recipe card) for the key component.
- **Signature interaction**: one input that behaves in a way specific to the
  business (drag a ring to set a savings goal; slide a "dose clock" to schedule
  medication; tap a seat map to build a booking; fill a "fuel gauge" for
  progress).
- **Signature data view**: the key number or status shown in a form native to
  the domain (a tide-chart for a ferry service, a pill-box grid for medication
  adherence, a shelf view for inventory).
- **Signature motion**: a single orchestrated moment tied to the core outcome
  (the confirmation "stamp" when a booking is secured; the plant growing one
  stage when a habit is logged).
- **Signature rhythm**: an unusual but logical layout structure that follows the
  user's real-world process (a vertical "journey line" that all screens hang
  from).

**Uniqueness test** (do this before building): if you swapped the logo and copy
for a competitor in a different industry and the design still worked, it is
generic. Revisit. Also avoid the clustered defaults listed in
`references/anti-patterns.md`.

**Accessibility test for the signature**: it must have a keyboard path, a
screen-reader equivalent, and a no-motion version. A signature that excludes
people is a failed signature.

### Phase 3: Choose tokens (colour, type, shape, space)

Define tokens once, as CSS custom properties, then use only tokens.
A starter token file is in `references/patterns.md`.

#### Colour: friendly, harmonious, accessible

Build palettes in perceptual terms (OKLCH, or HSL if tooling demands it) so
lightness steps are even and contrast is predictable.

1. **Pick the emotional register from the domain and user state**, not from
   habit:
   - Calm and trust (health, finance, legal, government): desaturated blues,
     teals, sea-greens, with warm neutrals to avoid clinical coldness.
   - Energy and appetite (food, fitness, events): warm hues (coral, saffron,
     chilli), balanced by deep, dark neutrals for text.
   - Growth and care (education, agriculture, sustainability, wellness): greens
     and soft yellows, earthy browns, with one lively accent.
   - Focus and precision (developer tools, analytics, logistics): restrained
     neutrals with one saturated signal colour reserved for action and status.
   - Play and imagination (kids, games, creative tools): higher saturation but
     keep text surfaces calm; vary hues, not just brightness.
   - Consider the local culture: colour meanings differ by region. Check the
     user's market (for example, white and red carry different associations in
     different countries) and avoid accidental negative signals.
2. **Structure**: 1 base hue family for brand, 1 accent (contrasting or
   triadic) used sparingly (about 10%), tinted neutrals (a hint of brand hue
   in greys, never pure #000 or #FFF as dominant surfaces), plus semantic
   colours (success, warning, danger, info).
3. **Ratios**: roughly 60% surface/neutral, 30% secondary/brand, 10% accent.
   Large coloured areas should be soft; saturation lives in small, important
   things (primary button, active state, the signature element).
4. **Contrast floor**: body text 4.5:1 or better, large text (24px, or 18.66px
   bold) and UI component boundaries/icons 3:1 or better. Aim above the floor
   for body text (7:1 on the main reading surface when feasible). Check
   hover, disabled-adjacent, placeholder, and text-on-image cases too.
5. **Never use colour alone** to convey meaning. Pair status colours with an
   icon and a text label. Test the palette in greyscale and with
   deuteranopia/protanopia simulation: success and danger must differ in
   lightness and icon, not just red vs green.
6. **Dark mode and high contrast**: define a second token set under
   `prefers-color-scheme: dark`; do not just invert. Reduce saturation on dark
   surfaces, lift surface elevation with lighter tints, not shadows. Respect
   `forced-colors: active` (use system colours for borders and focus).
7. **Friendly hues**: prefer slightly warm, slightly desaturated mid-tones for
   large surfaces; avoid pure neon on large areas; avoid red-on-blue vibration;
   keep a visible "rest" colour so eyes have somewhere to land.

#### Typography

- One or two families, clearly distinct if two. Choose for the domain's
  personality and for legibility at small sizes and on low-end screens. Do not
  default to the same few families for every project.
- Fluid scale with `clamp()`; body at least 16px (1rem); line-height 1.5 or
  more for body; line length 45 to 75 characters.
- Use `rem` so user font-size settings work; never block zoom to 200%+.
- Numerals matter in business UIs: use tabular figures for money, quantities,
  and tables so columns align.
- Headings follow a real outline (one h1, no skipped levels); style with
  classes, not by choosing the wrong tag.

#### Shape, space, elevation

- Choose a shape language from the domain (soft and rounded for care; crisp for
  precision; chunky for play) and apply it with a *hierarchy* of radii, not one
  radius everywhere.
- 4px or 8px spacing scale; generous padding around primary actions; group
  related things with proximity before reaching for borders.
- Minimum touch target 44x44 CSS px (24x24 is the WCAG 2.2 absolute floor, but
  aim for 44 on mobile) with spacing between adjacent targets.

### Phase 4: Write the Design Brief

Before the code, give the user a compact brief (10 to 15 lines):

```
Domain & users:   <one line>
Primary job:      <one line>
Key rules → UI:   <2-4 rules and how each shows up>
Signature:        <the one memorable idea + its accessible fallback>
Palette:          <4-6 named hex values, and why this register>
Type & shape:     <families, scale, radius language>
Layout:           <concept in one sentence + simple ASCII wireframe>
Assumptions:      <anything you inferred>
```

Then check it against the uniqueness test. If any part reads like what you'd
produce for any similar business, revise it, and say what you changed.

### Phase 5: Build

Use semantic HTML first, then CSS, then the minimum JavaScript. Match the
user's stack if they named one (React, Vue, Tailwind, etc.); otherwise default
to a single self-contained HTML file or a React component, depending on how
interactive it is. Follow the sections below.

### Phase 6: Critique and refine

Run the **Final Checklist** at the end. Fix what fails, then remove one
decoration (the "take off one accessory" rule). Summarise for the user in a few
sentences: what the signature is, what business rules shaped the UI, and any
assumptions to confirm.

---

## Layout and responsiveness

- **Mobile-first**, then enhance. Design the smallest screen's content order
  first; it forces priority decisions.
- Use CSS Grid and Flexbox with `minmax()`, `auto-fit`, `gap`, and `clamp()`
  rather than many fixed breakpoints. Where the component, not the page,
  decides layout, use **container queries**.
- Use logical properties (`margin-inline`, `padding-block`, `inset-inline-start`)
  so RTL languages work for free. Never hard-code left/right when the meaning is
  start/end.
- Reflow at 320px width with no horizontal scrolling (except data tables, code,
  and maps inside their own scroll container). Content must work at 400% zoom.
- Keep the primary action in the thumb zone on mobile (bottom sheet or sticky
  bar, padded with `env(safe-area-inset-bottom)`). Don't let sticky bars cover
  focused fields.
- Tables on small screens: convert to labelled cards, or keep a table with a
  sticky first column inside a focusable, labelled scroll region.
- Don't hide critical information on mobile; reorder or collapse it
  (progressive disclosure) instead.
- Use `100dvh`/`svh` rather than `100vh` for full-screen layouts on mobile.
- Respect `prefers-reduced-motion`, `prefers-color-scheme`,
  `prefers-contrast`, and `forced-colors`.
- Provide a skip link, landmarks (`header`, `nav`, `main`, `aside`, `footer`),
  and a logical DOM order that matches the visual order.

## Forms: where business logic and UX meet

Forms are where most users succeed or give up. Design them from the rules.

**Structure**
- Ask only for what the business rules truly need. Every field must trace to a
  rule or a workflow step; delete the rest.
- Group fields by the user's mental model, not the database table. One column
  by default; side-by-side only for tightly related pairs (day/month/year,
  city/postcode).
- Long processes become steps with a visible progress indicator, a "review and
  confirm" step for risky actions, and the ability to go back without data
  loss. Save drafts automatically where the cost of losing data is high.
- Use **progressive disclosure for conditional rules**: show a follow-up field
  only when its trigger applies, announce the change to screen readers
  (`aria-live="polite"` region or move focus sensibly), and never shift layout
  under the user's cursor without cause.

**Fields**
- A visible `<label>` for every control, always above the field. Placeholders
  are examples, not labels. Mark optional fields as "(optional)" rather than
  marking every required one with an asterisk, unless most are optional.
- Connect hints and errors with `aria-describedby`. Put the rule *before* the
  mistake: "Password: at least 12 characters" beside the field, not only after
  failure.
- Use the right `type`, `inputmode`, and `autocomplete` tokens (`email`,
  `tel`, `one-time-code`, `postal-code`, `cc-number`, etc.) so mobile keyboards
  and autofill help.
- Prefer controls that make invalid input impossible: segmented controls,
  steppers with bounds, date pickers that grey out unavailable dates *with a
  reason*, searchable selects for long lists. Always keep a keyboard-usable
  fallback (e.g. a text input for dates).
- Don't use input masks that fight paste, don't clear fields on error, don't
  disable the submit button silently. If an action is unavailable, say what's
  missing.

**Validation and errors**
- Validate on blur (or on submit for the first attempt) and re-validate live
  once a field has been marked invalid. Never show an error while the user is
  still typing a valid prefix.
- On submit failure: show an error summary at the top (`role="alert"` or move
  focus to it) listing each problem as a link to its field, and mark each field
  with an inline message, an icon, and `aria-invalid="true"`.
- Error copy: say what happened and how to fix it, in plain language, no blame,
  no system jargon, no apology ("Enter a date after 1 March" rather than
  "Invalid input").
- Rule-based errors should expose the rule: "Refunds over 5,000 need manager
  approval. We'll send this for approval and notify you."

**Actions**
- Button labels are specific verbs ("Book appointment", "Send invoice"), and
  the same word is used in the confirmation message.
- One clear primary action; secondary actions visually quieter; destructive
  actions separated, coloured as danger *and* labelled, with confirmation that
  restates the consequence, or better, an undo.
- Show progress and prevent double submission (disable after press, with a
  visible "Saving..." status announced politely). Confirm success with a clear
  next step.

## Components: model every state

For each component, design and build **all** of these states, not just the happy
path: default, hover, focus-visible, active, disabled (with reason), loading,
empty, error, success, partial/out-of-range, and read-only.

- **Status components come from the entity lifecycle.** Build one reusable
  status pill/timeline whose variants match the real states of the business
  object (not generic "success/warning"), each with icon + text + colour.
- **Empty states are onboarding**: say what belongs here, why it's empty, and
  offer the next action.
- **Loading**: skeletons that match final layout; announce long loads; avoid
  spinners that give no duration cue for slow processes (show steps instead).
- **Disabled with a reason**: use `aria-disabled="true"` plus visible,
  associated explanation when the user might otherwise be confused why they
  cannot proceed.
- **Permissions**: hide what a role should never see; show-but-explain what
  they might reasonably expect but can't do.
- **Tables and lists**: sortable headers that are real buttons with
  `aria-sort`, filters that mirror real business categories, saved views for
  expert users, bulk actions that state counts ("Archive 12 invoices").
- **Navigation**: name items by user tasks, keep the structure shallow,
  indicate the current location (`aria-current`), and keep it identical across
  pages.
- **Modals/drawers**: use the native `<dialog>` or a well-implemented pattern:
  focus moves in, is trapped, Escape closes, focus returns to the trigger,
  background is inert. Prefer inline or page flows for complex tasks.
- **Custom widgets** (tabs, comboboxes, menus, sliders): follow the WAI-ARIA
  Authoring Practices keyboard model exactly, or use native elements. No ARIA is
  better than bad ARIA.

## Grabbing attention without hurting usability

Attention is a budget: spend it on the primary job and the signature.

- **Establish one focal point per screen** using size, contrast, and whitespace.
  If everything is highlighted, nothing is.
- **Open with the domain's most characteristic thing** (a live availability
  view, the user's next appointment, the day's route), not a generic hero
  slogan.
- **Motion**: use it to explain change (something moved, expanded, was saved),
  or for the one signature moment on load. Durations 150 to 300ms for
  interface feedback; easing that decelerates in. No parallax or looping
  animation near text. Provide a reduced-motion alternative that keeps the
  information (e.g. a crossfade or an instant state change with a text
  confirmation).
- **Microcopy** carries personality: plain verbs, sentence case, specific,
  consistent vocabulary from the domain's own language. Errors and empty
  states are where tone earns trust.
- **Delight lives in moments of success**, such as a completed booking or
  submitted claim, not in the flows where users are trying to get something
  done quickly.
- **Perceived speed**: optimistic updates where safe, instant feedback on
  press (under 100ms), skeletons, and pre-filled defaults based on logic
  (remember last address, suggest likely options).

## Accessibility floor (WCAG 2.2 AA)

Build these in from the first line, not at the end:

- Semantic elements before ARIA; correct names, roles, and states for custom
  controls; `lang` attribute on `html` (and on foreign-language passages).
- **Keyboard**: every interaction works with Tab, Shift+Tab, Enter, Space,
  Arrow keys, Escape; no keyboard traps; logical order; visible
  `:focus-visible` indicator (at least 2px, 3:1 contrast against adjacent
  colours, not hidden by sticky headers: use `scroll-margin`/`scroll-padding`).
- **Pointer**: no path-based gestures as the only option; drag interactions
  need a single-pointer alternative (buttons, inputs); targets large enough.
- **Text alternatives**: meaningful `alt` text for informative images, empty
  `alt` for decorative; charts have a text summary or a data table; icons-only
  buttons have accessible names.
- **Status messages**: use `role="status"` / `aria-live="polite"` for non-urgent
  updates (saved, filters applied, 12 results) and `role="alert"` only for
  errors that need immediate attention.
- **Time and motion**: no auto-advancing content without pause control; session
  timeouts warn and allow extension; nothing flashes more than 3 times a
  second.
- **Consistent help** (WCAG 2.2): keep help links/contact in the same place on
  every page; don't ask users to re-enter information they've already given in
  the same flow (redundant entry); offer accessible authentication (allow paste
  and password managers, no cognitive-puzzle-only logins).
- **Readability**: plain language, short sentences for critical instructions,
  define jargon, avoid justified text and ALL-CAPS paragraphs.
- Zoom to 200% and 400% reflow, text-spacing overrides, and orientation
  (don't lock portrait or landscape) must all keep working.

## Final checklist

Run through this before handing over. Fix failures, don't just report them.

**Domain & logic**
- [ ] Every screen has one obvious primary action tied to the user's real job.
- [ ] Business rules are visible *before* they can be violated.
- [ ] Entity states match the business's real lifecycle and vocabulary.
- [ ] Risky or irreversible actions have review, confirmation, or undo.

**Uniqueness**
- [ ] There is exactly one signature element, rooted in the domain.
- [ ] Swapping to a different industry would break the design (not generic).
- [ ] No unexplained decoration; at least one thing was removed.

**Accessibility**
- [ ] Full keyboard operation with visible focus; no traps.
- [ ] Contrast meets 4.5:1 text / 3:1 UI; meaning never relies on colour alone.
- [ ] Labels, hints, errors programmatically associated; error summary works.
- [ ] Headings and landmarks make sense; screen-reader names are correct.
- [ ] Reduced-motion, dark, high-contrast, and 200%/400% zoom all hold up.
- [ ] Targets are at least 44px on touch layouts.

**Responsiveness**
- [ ] Works at 320px through large desktop with no horizontal page scroll.
- [ ] Logical properties used; RTL won't break the layout.
- [ ] Tables, modals, and sticky elements behave on small screens.

**Experience**
- [ ] Empty, loading, error, success, and disabled states all designed.
- [ ] Copy is plain, specific, consistent, and from the user's perspective.
- [ ] Motion explains change or serves the signature; nothing loops needlessly.

## Reference files

- `references/patterns.md`: starter token CSS (colour, type, space, focus,
  reduced motion, forced colours), an accessible form pattern with error
  summary, a status-pill pattern, and domain-to-signature examples. Read this
  when you start building.
- `references/anti-patterns.md`: generic defaults to avoid, plus common
  accessibility and form mistakes. Read it during the uniqueness test and the
  final critique.
