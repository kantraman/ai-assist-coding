# Anti-patterns

Use during the uniqueness test (Phase 2) and the final critique (Phase 6).

## Generic design defaults to avoid (unless the brief demands them)

- Cream background + high-contrast serif + terracotta accent.
- Near-black background + one acid-green or vermilion accent.
- Newspaper layout: hairline rules, zero radius, dense columns, for a business
  that has nothing to do with publishing.
- The SaaS card kit: content chopped into identical rounded cards, the same
  radius and soft grey shadow on everything, gradient washes as decoration.
- Template chrome: tracked-out ALL-CAPS eyebrow above every heading, "A · B · C"
  meta strings, spaced em-dash labels, monospace small labels, arrows appended
  to every button.
- A centred hero with a big number, three feature cards, and a gradient CTA.
- Scattered fade-and-slide entrances on every section; hover lifts on every
  card.
- Stock illustrations of abstract people holding oversized phones.
- Numbered steps (01 / 02 / 03) when the content isn't truly a sequence.

## Domain-blind mistakes

- Using internal field names or status codes as labels ("status_id 4").
- One generic "success/warning/error" system when the business has its own
  lifecycle states.
- Hiding business rules until submission fails.
- Same layout for a first-time visitor and an expert doing the task fifty times
  a day (offer shortcuts, saved views, bulk actions for experts).
- Designing only the happy path: no empty, partial, offline, slow, or failed
  states.

## Accessibility mistakes

- Placeholder text used as the label.
- Removing the focus outline without a replacement.
- Colour-only status (red/green dots with no text or icon).
- Custom dropdowns, tabs, or modals without proper roles, keyboard behaviour,
  and focus management.
- Click targets under 24px, or tightly packed small icon buttons.
- Disabling zoom (`user-scalable=no`) or fixing font sizes in `px`.
- Error messages that vanish after a timeout or appear only as colour change.
- Auto-playing carousels or video with motion and no pause.
- Drag-only interactions with no button or input alternative.
- Text over images without a guaranteed-contrast scrim.
- Hover-only tooltips and menus (unreachable by keyboard and touch).
- Time-limited sessions that lose user input without warning.
- `div` and `span` buttons.

## Form mistakes

- Asking for data nobody uses; splitting a name field into five when one works.
- Required-asterisks everywhere with no legend; no "(optional)" markers.
- Validating while the user is still typing; showing errors before interaction.
- Clearing the form after an error.
- Disabled submit button with no explanation.
- Password rules revealed only after failure; blocked paste in password or
  one-time-code fields.
- Date inputs that demand a specific typed format without showing it.
- Modal confirmations that say "Are you sure?" instead of restating the
  consequence ("Delete 3 patient records? This can't be undone.").
- Long forms without progress, saving, or review.

## Motion and delight mistakes

- Several competing animations with no single focal moment.
- Animation that blocks use (waiting for an entrance to finish before a button
  works).
- Celebrations (confetti) on routine or serious actions.
- Ignoring `prefers-reduced-motion`.
