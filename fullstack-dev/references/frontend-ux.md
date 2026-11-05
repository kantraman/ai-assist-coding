# Frontend UI/UX From Scratch

## Contents
1. Process
2. Design tokens (modular scale)
3. Layout and components
4. The state matrix
5. Accessibility
6. Performance
7. Data, state, forms
8. Testing
9. UX heuristics checklist

## 1. Process

1. **Users and jobs**: who, what job are they doing, what does success look like. One sentence per primary persona.
2. **Information architecture**: sitemap and navigation; name things in the user's words.
3. **Flows**: the 3 to 5 critical journeys as step lists, including failure paths. Cut steps relentlessly.
4. **Wireframes**: low fidelity first (text or simple layout). Decide hierarchy before color.
5. **Tokens**: color, type, spacing, radius, elevation, motion defined once.
6. **Components**: build smallest to largest (atoms to pages), each with all states.
7. **Polish and verify**: accessibility, performance, responsive checks, usability walkthrough with a real or imagined user.

For visual distinctiveness beyond functional UX (aesthetic direction, typography character), also use any design guidance the environment offers (a frontend-design skill, the project's existing design system).

## 2. Design tokens (modular scale, the fractal part)

One ratio generates every size, so the interface has consistent rhythm at every scale.

- **Type scale**: `size(n) = base * ratio^n` with ratio 1.2 (compact), 1.25 (default), 1.333 (editorial), or golden 1.618 (display-heavy). Body 16px minimum.
- **Spacing**: powers of the ratio or a 4/8 px grid; use the same few steps everywhere.
- **Line height**: 1.4 to 1.6 body, 1.1 to 1.3 headings. **Measure**: 45 to 75 characters.
- **Color**: neutral ramp (9 to 11 steps), one primary, semantic colors (success, warning, danger, info). Define light and dark values as tokens. Check every text/background pair for contrast.

Generate scales and verify contrast:

```bash
python scripts/design_tokens.py --base 16 --ratio 1.25 --steps 6 > tokens.css
python scripts/design_tokens.py --contrast "#1a1a1a" "#f5f5f5"    # WCAG ratio + AA/AAA verdict
```

## 3. Layout and components

- Mobile-first, fluid layouts (CSS grid/flex, `clamp()`), container queries for components; breakpoints from content, not devices.
- Components take data via typed props, emit events upward, own no global state unless they are the feature boundary. Keep presentational and data-fetching components separate (Core vs Adapters).
- Prefer an established accessible primitive library (Radix, Headless UI, React Aria, Angular CDK, native elements) over hand-rolled dialogs, menus, comboboxes.
- Use semantic HTML first (`button`, `nav`, `main`, `label`); ARIA only to fill gaps.

## 4. The state matrix

Every component and page that loads or changes data defines: **loading** (skeletons, not spinners for layout), **empty** (explain and offer the next action), **error** (what happened, how to recover, retry), **partial**, **success**, **disabled**, **offline/slow**, **permission denied**. Missing states are the most common source of "it feels broken".

## 5. Accessibility (target WCAG 2.2 AA)

Keyboard operable everywhere with visible focus; logical tab order; labels tied to inputs; text contrast 4.5:1 (3:1 large text and UI parts); do not rely on color alone; alt text for meaningful images; target size at least 24px (aim 44px on touch); respect `prefers-reduced-motion` and `prefers-color-scheme`; announce async changes with live regions; error messages linked to fields; page titles and heading hierarchy.

## 6. Performance (Core Web Vitals budgets)

LCP under 2.5 s, INP under 200 ms, CLS under 0.1. Tactics: ship less JS (route-level code splitting, tree shaking, avoid heavy deps), server rendering or static generation for content, responsive images with explicit dimensions and modern formats, font subsetting with `font-display: swap`, preload critical assets, virtualize long lists, debounce expensive handlers, memoize only after profiling. Set a bundle-size budget and fail CI when exceeded. Chunking and prefetch parameters are candidates for GA tuning.

## 7. Data, state, forms

- Server state via a query cache (TanStack Query, SWR, Apollo, framework loaders); client state minimal and local first, global only when shared.
- Optimistic updates only for low-risk actions with rollback.
- Forms: validate on blur and submit using the same schema as the API (shared types), show errors inline, preserve input on failure, prevent double submit, support autofill and paste.
- Never trust client checks for security; the server re-validates everything. Escape/encode output; avoid raw HTML injection; use a sanitizer if rich text is unavoidable.
- i18n: externalize strings early; avoid concatenated sentences; plan for text expansion and RTL.

## 8. Testing

Component tests (behavior via accessible queries), automated a11y checks (axe), visual regression for key screens, end-to-end for critical flows (Playwright/Cypress), and a Lighthouse/web-vitals check in CI. Test the state matrix, not just the happy path.

## 9. UX heuristics checklist

System status visible; match the user's language; easy undo and escape; consistency; error prevention before error messages; recognition over recall; flexibility for novices and experts; minimal, focused screens; helpful, specific errors; help available in context. One primary action per screen; destructive actions confirmed or undoable; defaults that are right for most users.
