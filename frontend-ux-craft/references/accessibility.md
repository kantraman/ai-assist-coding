# Accessibility: building it in, not bolting it on

Accessibility is the same job as good UX with fewer assumptions about the person: they might be on a
keyboard, a screen reader, a phone in sunlight, one hand, a slow connection, or just tired. Design for
the constrained case and the typical case gets better for free. Target **WCAG 2.2 AA** as the floor.

## Contents
1. Semantics first
2. Keyboard and focus
3. Names, labels, descriptions
4. Forms
5. Color, contrast, and not relying on either
6. Size, spacing, zoom, reflow
7. Motion and time
8. Dynamic content: live regions, dialogs, route changes
9. Complex widgets
10. Content: images, tables, charts, links
11. WCAG 2.2 additions people miss
12. Testing routine

---

## 1. Semantics first

The browser gives you keyboard support, focus behavior, and screen-reader roles for free when you use
the right element. ARIA is the repair kit for when native HTML can't express something, not the
starting point. (First rule of ARIA: if a native element does the job, use it. Bad ARIA is worse than none.)

| Need | Use | Not |
|---|---|---|
| Does something | `<button type="button">` | `<div onClick>` |
| Goes somewhere | `<a href>` (real URL, so open-in-new-tab and copy-link work) | `<button>` that calls `router.push` |
| Page regions | `<header> <nav> <main> <aside> <footer>`, one `<main>` | div soup |
| Headings | `<h1>`-`<h6>` in order, one `h1`; style with CSS, never pick a level for its size | `<div class="title">` |
| Lists of things | `<ul>/<ol>`, `<dl>` for label/value pairs | stacked divs |
| Tabular data | `<table>` with `<th scope>` and `<caption>` | CSS grid pretending |
| Modal | `<dialog>` + `showModal()` or a headless library | absolutely positioned div |
| Disclosure | `<details><summary>` | custom toggle with no state |
| Form fields | `<label for>` + `<input>` / `<select>` / `<textarea>` | placeholder as label |

If you must build a custom widget, look up its pattern in the WAI-ARIA Authoring Practices Guide and
implement **all** of it (roles, states, keyboard model), or use a headless library that already has
(Radix, React Aria, Reka UI, Headless UI, Angular CDK).

## 2. Keyboard and focus

- **Everything operable by keyboard, in a sensible order.** DOM order = visual order. Don't reorder
  with CSS `order`/grid placement in ways that make Tab jump around. Avoid positive `tabindex`.
- **Visible focus, always.** Never `outline: none` without a replacement. Use `:focus-visible`, a 2px
  ring with an offset, and ≥3:1 contrast against every background it can land on. Match it to the
  brand; a designed focus ring is a mark of a considered UI.
- **Skip link** as the first focusable element (`<a href="#main">Skip to content</a>`), visible on focus.
- **Move focus deliberately** when the UI changes under the person:
  - Open dialog → focus first meaningful control (or the dialog title if content is long); trap focus
    inside; `Esc` closes; on close, return focus to the trigger.
  - Delete an item from a list → focus the next item (or the list heading if none left), not `<body>`.
  - Client-side route change → move focus to the new page's `<h1>` (give it `tabindex="-1"`), update
    `document.title`, announce if needed. SPA routers don't do this for you.
  - Form submit with errors → focus the error summary or first invalid field.
- **Roving tabindex / `aria-activedescendant`** for composite widgets (tabs, menus, listboxes, toolbars,
  grids): one Tab stop into the widget, arrow keys inside.
- No keyboard traps. Use `inert` on background content behind modals instead of hand-rolled traps when you can.
- Custom shortcuts must be single-key-safe: allow turning off or remapping, or require a modifier (WCAG 2.1.4).

## 3. Names, labels, descriptions

Every interactive element needs an **accessible name** that matches what's visible.

- Visible text label first. `aria-label` only when there's no visible text (icon buttons): `aria-label="Delete invoice 1042"`, specific, not "Delete".
- Label-in-name rule: if the button *shows* "Search", its accessible name must contain "Search" (voice-control users say what they see).
- Hints and errors attach with `aria-describedby`, not by proximity.
- Decorative icons: `aria-hidden="true"` (and `focusable="false"` on inline SVG). Informative icons get a text alternative.
- Link text makes sense out of context ("View invoice 1042", not "Click here" or five identical "Read more").
- State lives in attributes, not just classes: `aria-expanded`, `aria-pressed`, `aria-current="page"`, `aria-selected`, `aria-invalid`, `aria-busy`, `disabled`.
- Set `lang` on `<html>` and on foreign-language snippets.

## 4. Forms

Forms are where most products lose people. Make them boringly excellent.

- Visible `<label>` above the field. Placeholder is an example, never the label (it vanishes, has poor contrast, and isn't reliably announced).
- Mark **optional** fields rather than asterisking required ones when most are required; if using `*`, explain it once. Use `required` + `aria-required` sparingly and consistently.
- Correct `type`, `inputmode`, and **`autocomplete`** tokens (`given-name`, `email`, `one-time-code`, `street-address`, `new-password`, `current-password`). It's a WCAG requirement (1.3.5) and a huge UX win.
- **Validate on blur or submit, not on every keystroke.** Exception: helpful live feedback (password strength, character count) that never shows an error before the person has had a chance.
- Errors: text (not color alone) + icon, next to the field, plain language, say how to fix it. Keep the person's input. Link them in `aria-describedby`, set `aria-invalid="true"`.
- On submit failure, show an error summary at the top with links to each field and move focus to it, or focus the first invalid field.
- Don't disable the submit button as a validation strategy; it hides *why*. Let them press it and explain. Do disable/`aria-busy` **while submitting** to prevent double-sends, and keep the label ("Saving…").
- Group related controls in `<fieldset><legend>`; radios and checkbox groups always.
- Don't block paste in password or OTP fields. Support password managers. (WCAG 3.3.8 Accessible Authentication.)
- Don't ask for the same info twice in one flow (3.3.7 Redundant Entry). Prefill and let them edit.
- Long forms: save progress, show what's left, allow going back without loss.
- Time limits: warn, allow extension, never silently destroy work.

## 5. Color, contrast, and not relying on either

- Text: **4.5:1** (3:1 for ≥24px or ≥18.66px bold). UI components, icons that carry meaning, focus rings, input borders: **3:1** against adjacent colors.
- Verify with `scripts/contrast.py` / `scripts/check_tokens.py`. Don't eyeball it, and don't trust a single design-tool plugin for OKLCH colors.
- **Never color alone.** Error = color + icon + text. Chart series = color + shape/pattern/direct label. Links inside body text = color + underline. Required = text, not just red.
- Test in **dark mode**, **forced-colors** (Windows High Contrast), and grayscale. `box-shadow`-only borders and background-image icons disappear in forced-colors; use real `border`/`outline` or `currentColor` SVG.
- Respect `prefers-color-scheme` and offer a manual override; respect `prefers-contrast: more` where cheap (thicken borders, raise muted text).
- Disabled controls are exempt from contrast rules, but don't make them unreadable. Prefer explaining *why* something is unavailable.

## 6. Size, spacing, zoom, reflow

- **Targets:** ≥24×24 CSS px is the WCAG 2.2 floor (2.5.8); design for **44×44** on touch. Small visuals can have larger hit areas via padding or pseudo-elements. Keep adjacent targets separated.
- Text in `rem`, never fixed `px` for body copy. It must scale to **200%** without loss and the layout must **reflow at 320px width / 400% zoom** with no two-dimensional scrolling (except data tables, maps, code).
- Don't disable pinch-zoom (`user-scalable=no`, `maximum-scale=1`). Ever.
- Survive user text-spacing overrides (line-height 1.5, letter-spacing .12em, word-spacing .16em): no fixed heights on text containers; use `min-height`.
- Line length ≤ ~75 characters for prose, `line-height` ≥ 1.5 for body.

## 7. Motion and time

- Honor `prefers-reduced-motion: reduce`: remove parallax, large translations, auto-playing loops, and scroll-jacking. Keep tiny opacity/color transitions that convey state.
- Nothing flashes more than 3 times per second.
- Auto-updating, moving, or blinking content lasting >5s needs pause/stop/hide. Carousels: no autoplay by default.
- Toasts: don't auto-dismiss anything that needs action or contains critical information; pause dismiss timer on hover and focus; make them reachable (not only visible for 3 seconds); ≥5-8s plus length-based time. Prefer inline feedback when the person is already looking at the spot.

## 8. Dynamic content: live regions, dialogs, route changes

- **Status messages** ("Saved", "3 results", "Copied") go in a persistent live region that exists in the DOM *before* the message changes: `role="status"` (polite) or `role="alert"` (assertive, for errors only). Inject text into it; don't mount a new region with the text already inside.
- Loading: `aria-busy="true"` on the region being updated, plus a text announcement when done. Skeletons are visual; give the container an accessible "Loading invoices…" label.
- Infinite scroll: provide a "Load more" button or pagination alternative; keep the footer reachable.
- Dialogs: `role="dialog"` (or `alertdialog` for confirmations that interrupt), `aria-modal="true"`, labelled by its title, described by its body if short.
- Route changes: update `<title>` (unique, most specific first: "Invoice 1042 · Billing · Acme"), move focus, optionally announce.

## 9. Complex widgets: quick rules

- **Tabs:** `tablist/tab/tabpanel`, arrows move between tabs, Tab moves into the panel. Don't use tabs for navigation between URLs; use links.
- **Menus** (`role="menu"`) are for application-style action menus, *not* site navigation. Site nav is a list of links in `<nav>` (a disclosure button can reveal sub-lists).
- **Combobox / autocomplete:** `role="combobox"` + `aria-expanded` + `aria-controls` + `aria-activedescendant`; announce result counts via live region. Prefer a headless lib.
- **Data grids:** only when you truly need spreadsheet-style navigation. A plain `<table>` with sortable header buttons (`aria-sort`) is far more robust.
- **Drag and drop:** always offer a non-drag alternative (buttons: "Move up/down", or a "Move to…" menu). WCAG 2.5.7.
- **Tooltips:** supplemental only, never the sole home of essential information; reachable by keyboard focus; dismissible with `Esc`; hoverable. Touch has no hover, so put important help in the UI itself.
- **Custom selects, date pickers:** default to the native control unless there's a real reason. Native pickers are accessible, localized, and correct on mobile.

## 10. Content: images, tables, charts, links

- `alt` describes purpose, not pixels. Decorative → `alt=""`. Images of text: avoid. Logos: the org name. Complex images: short alt + longer description nearby.
- Data tables: `<caption>`, `<th scope="col|row">`; don't nest layout tables; responsive collapse must keep semantics (or provide a card list alternative).
- Charts: title + summary sentence of the takeaway; a data table alternative; direct labels; patterns or shapes in addition to color; don't rely on hover for values.
- Video/audio: captions, transcripts, no autoplay with sound, controls that are keyboard accessible.
- Icons-only navigation is a usability cost even when accessible. Add labels unless the icon is universal (search, close).

## 11. WCAG 2.2 additions people miss

| SC | What it asks | Practical rule |
|---|---|---|
| 2.4.11 Focus Not Obscured | Focused control isn't fully hidden by sticky headers/cookie bars | Use `scroll-padding-top`/`scroll-margin` equal to sticky bar height |
| 2.5.7 Dragging Movements | Every drag has a single-pointer alternative | Buttons or menus for reorder/move |
| 2.5.8 Target Size (Min) | 24×24 px (with spacing exceptions) | Aim 44px on touch |
| 3.2.6 Consistent Help | Help/contact is in the same place across pages | Put it in the shared layout |
| 3.3.7 Redundant Entry | Don't make people retype info they already gave | Prefill / "Same as billing" |
| 3.3.8 Accessible Authentication | No cognitive tests (remembering, transcribing) to log in | Allow paste + password managers, offer passkeys / email links |

## 12. Testing routine (do it every time UI is built)

Run this as part of finishing, not as a phase after.

1. **Keyboard only:** Tab through the entire flow. Can you reach and operate everything? Is focus always visible and never lost? Does Esc close things? Is order logical?
2. **Zoom/reflow:** 200% browser zoom and 320px viewport. Nothing clipped, overlapped, or sideways-scrolling.
3. **Contrast:** run the checker on tokens; spot-check text over images/gradients.
4. **Screen reader smoke test:** NVDA+Firefox/Chrome (Windows), VoiceOver+Safari (macOS/iOS), TalkBack (Android). Landmarks, headings list, form labels, error announcements, dialog open/close, route change.
5. **Reduced motion + dark mode + forced-colors** toggled.
6. **Automated:** axe-core / Lighthouse / `eslint-plugin-jsx-a11y` / `angular-eslint` template a11y rules / `eslint-plugin-vuejs-accessibility`. These catch ~30-40% of issues; they don't replace steps 1-4.
7. **Real states:** empty, loading, error, long text, many items, RTL if supported.

When you can't run these (no browser available), say so and list which of these the person should verify, rather than claiming compliance.
