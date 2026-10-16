# Patterns and starters

Contents
1. Token starter (CSS)
2. Accessible form pattern with error summary
3. Status pill from an entity lifecycle
4. Domain-to-signature examples
5. Palette recipes by domain register

---

## 1. Token starter (CSS)

Replace every value with choices made for the specific domain. The structure is
what matters: tokens, tinted neutrals, semantic colours, fluid type, focus,
motion and contrast preferences.

```css
:root {
  color-scheme: light dark;

  /* Brand + accent: pick from the domain, not from habit */
  --brand-600: oklch(48% 0.09 200);
  --brand-100: oklch(94% 0.03 200);
  --accent-500: oklch(72% 0.16 55);          /* ~10% of the UI */

  /* Tinted neutrals (a hint of brand hue; never pure black/white surfaces) */
  --ink-900: oklch(22% 0.02 200);
  --ink-600: oklch(42% 0.02 200);
  --surface-0: oklch(98.5% 0.006 90);
  --surface-1: oklch(96% 0.01 90);
  --line: oklch(86% 0.01 200);

  /* Semantic: always pair with icon + text */
  --success: oklch(45% 0.11 155);
  --warning: oklch(52% 0.12 75);
  --danger:  oklch(48% 0.17 25);
  --info:    oklch(47% 0.10 250);

  /* Type: fluid, rem-based */
  --font-body: "Your Body Face", system-ui, sans-serif;
  --font-display: "Your Display Face", Georgia, serif;
  --step-0: clamp(1rem, 0.96rem + 0.2vw, 1.125rem);
  --step-1: clamp(1.25rem, 1.15rem + 0.5vw, 1.5rem);
  --step-3: clamp(2rem, 1.6rem + 2vw, 3rem);

  /* Space: 4px base */
  --s-1: 0.25rem; --s-2: 0.5rem; --s-3: 0.75rem; --s-4: 1rem;
  --s-6: 1.5rem;  --s-8: 2rem;   --s-12: 3rem;

  /* Radius hierarchy (not one radius for everything) */
  --r-control: 0.5rem; --r-card: 1rem; --r-feature: 1.75rem;

  --focus: oklch(55% 0.2 260);
  --target: 2.75rem; /* 44px */
}

@media (prefers-color-scheme: dark) {
  :root {
    --ink-900: oklch(94% 0.01 200);
    --ink-600: oklch(78% 0.015 200);
    --surface-0: oklch(20% 0.015 200);
    --surface-1: oklch(25% 0.015 200);
    --line: oklch(36% 0.015 200);
    --brand-600: oklch(78% 0.09 200);
    --brand-100: oklch(30% 0.03 200);
    --success: oklch(78% 0.12 155);
    --warning: oklch(80% 0.12 75);
    --danger:  oklch(75% 0.14 25);
    --info:    oklch(78% 0.09 250);
    --focus:   oklch(80% 0.14 260);
  }
}

html { scroll-padding-top: 5rem; }   /* sticky header never hides focus */
body {
  margin: 0;
  font: var(--step-0)/1.55 var(--font-body);
  color: var(--ink-900);
  background: var(--surface-0);
}

:where(a, button, input, select, textarea, summary, [tabindex]):focus-visible {
  outline: 3px solid var(--focus);
  outline-offset: 3px;
  border-radius: 4px;
}

button, [role="button"], input, select, textarea { min-height: var(--target); }

.tabular { font-variant-numeric: tabular-nums; }

.visually-hidden {
  position: absolute; width: 1px; height: 1px; overflow: hidden;
  clip-path: inset(50%); white-space: nowrap;
}

.skip-link { position: absolute; inset-inline-start: var(--s-4); top: -4rem; }
.skip-link:focus { top: var(--s-4); }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

@media (forced-colors: active) {
  .status, .card { border: 1px solid CanvasText; }
  :focus-visible { outline-color: Highlight; }
}
```

Verify contrast numerically for the actual values you pick; the examples above
are structure, not guaranteed-passing colours.

---

## 2. Accessible form pattern with error summary

```html
<form novalidate aria-labelledby="form-title">
  <h1 id="form-title">Book a consultation</h1>

  <!-- Shown only after a failed submit; focus moves here -->
  <div id="error-summary" role="alert" tabindex="-1" hidden>
    <h2>Fix 2 things to continue</h2>
    <ul>
      <li><a href="#phone">Enter a phone number we can reach you on</a></li>
      <li><a href="#date">Choose a date at least 24 hours from now</a></li>
    </ul>
  </div>

  <div class="field">
    <label for="phone">Mobile number</label>
    <p id="phone-hint" class="hint">We text a reminder the day before.</p>
    <input id="phone" name="phone" type="tel" inputmode="tel"
           autocomplete="tel" aria-describedby="phone-hint phone-error"
           aria-invalid="true" required>
    <p id="phone-error" class="error">
      <svg aria-hidden="true" width="16" height="16"><!-- icon --></svg>
      Enter a phone number we can reach you on.
    </p>
  </div>

  <fieldset>
    <legend>How should we confirm?</legend>
    <label><input type="radio" name="confirm" value="sms"> Text message</label>
    <label><input type="radio" name="confirm" value="email"> Email</label>
  </fieldset>

  <!-- Conditional field: announce its appearance -->
  <div id="email-wrap" hidden>
    <label for="email">Email address</label>
    <input id="email" name="email" type="email" autocomplete="email">
  </div>
  <p class="visually-hidden" role="status" id="live"></p>

  <button type="submit">Book consultation</button>
</form>
```

Behaviour notes:
- Validate on blur, then live once a field is invalid.
- On failed submit: build the summary, unhide it, `focus()` it, keep all
  entered values.
- When a conditional field appears, set the live region text ("Email address
  field added") rather than stealing focus.
- On success: a confirmation that repeats the action verb ("Consultation
  booked"), states the key facts (date, time, place), and gives the next step.

---

## 3. Status pill from an entity lifecycle

Map **the business's real states**, each with colour, icon and text:

```html
<span class="status status--packed">
  <svg aria-hidden="true"><!-- box icon --></svg>
  Packed
</span>
```

```css
.status {
  display: inline-flex; align-items: center; gap: var(--s-2);
  padding: 0.25rem 0.75rem; border-radius: 999px;
  font-weight: 600; font-size: 0.875rem;
  border: 1px solid currentColor;
  background: color-mix(in oklch, currentColor 10%, var(--surface-0));
}
.status--delivered { color: var(--success); }
.status--delayed   { color: var(--warning); }
.status--failed    { color: var(--danger); }
```

For lifecycles with order (draft, submitted, approved, paid), also render a
timeline: an ordered list (`<ol>`) with `aria-current="step"` on the active item
and visually hidden text such as "completed" / "current" / "upcoming".

---

## 4. Domain-to-signature examples

Starting points only. The real signature must come from the actual business.

| Domain | Signature idea | Accessible fallback |
|---|---|---|
| Neighbourhood clinic | Appointment slots as a soft "day dial" showing when the doctor is free, with the user's usual time highlighted | Plain list of times as radio buttons |
| Ferry / bus operator | Departure board whose rows ease like tide tables; delays shown as a shifting wave line | Table with text status and relative time |
| Community bank / savings group | Goal "jar" that fills as contributions arrive; rules (lock-in period) shown as a visible lid | Progress element with numeric values |
| Restaurant / food ordering | Menu as a stacked "order slip" that grows as items are added; allergens as stamped marks on the slip | List with allergen text labels |
| School / tutoring | Weekly timetable as a woven pattern where each subject has its own thread | Day-by-day agenda list |
| Farm / agri marketplace | Listings as seed-packet cards with sowing and harvest windows drawn as arcs | Text date ranges |
| Legal / consent forms | A "clause ribbon" that shows where you are in the document and what each clause means in plain language | Heading structure + plain summary |
| Logistics / delivery | Route as a single vertical journey line every screen hangs from, with the next stop pulsing once | Ordered list with ETA text |

Pick *one*. A product with five signatures has none.

---

## 5. Palette recipes by domain register

Use as hue-direction guidance, then tune lightness for contrast. Do not copy
these verbatim; the aim is a palette that is specific to the brief.

- **Calm trust (health, finance)**: sea-glass teal base, warm sand surfaces,
  one apricot accent, ink with a blue tint.
- **Appetite and warmth (food, events)**: deep aubergine or espresso text,
  turmeric or chilli accent, warm off-white surfaces; keep large areas soft.
- **Growth and care (education, agri, wellness)**: moss and fern greens, clay
  and oat neutrals, a small citrus accent for action.
- **Focus (analytics, ops)**: cool slate neutrals with one saturated signal hue
  for action; separate success/warning/danger by lightness as well as hue.
- **Play (kids, games)**: three or four hues of similar lightness for variety,
  calm cream or pale lavender surfaces for text, rounded shapes, bold but
  well-contrasted labels.
- **Public service (government, utilities)**: deep, dependable blue or green,
  plenty of white space, extremely high contrast, plain-language copy, large
  type and touch targets.

Always validate: text contrast, UI-component contrast, greyscale legibility,
colour-blindness simulation, dark-mode variant.
