# Layout, object placement, and responsive design

Layout answers three questions on every screen: *What is this for? What do I do next? Where am I?*
Consistent **placement** is what lets people stop thinking about the interface. If the primary
action, the page title, and the filters live in the same place on every screen, the product feels
learnable, trustworthy, and fast.

## Contents
1. Principles
2. Spacing and rhythm
3. Grid, containers, and breakpoints
4. The placement contract
5. Page patterns (with wireframes)
6. Responsive transformations, by component
7. Touch and thumb reach
8. Robustness: content, overflow, i18n
9. Modern CSS toolbox
10. Test matrix

---

## 1. Principles

1. **Proximity is the strongest grouping signal.** Space *between* groups must be visibly larger than space *within* groups (a 2:1 ratio is a good starting point). Fix crowded UIs with spacing before adding lines and boxes.
2. **Hierarchy through size, weight, and space** before color. If it only reads as important because it's blue, it isn't structurally important.
3. **Alignment lines are structure.** Fewer distinct left edges = calmer page. Align labels, inputs, and buttons to shared edges; align baselines for text in a row.
4. **Left-align text** (in LTR). Center only short, standalone, ceremonial content (empty state, success message, a single headline). Centered paragraphs and centered forms are harder to scan.
5. **Content decides breakpoints**, not device names. Widen the window until the layout starts to strain, then add a breakpoint there.
6. **Mobile-first, then enhance.** Start with the single-column reading order (it's also the accessibility order), then rearrange with grid at wider sizes, without changing DOM order.
7. **One clear next step per screen.** The eye should land on the primary action or primary content within a second.
8. **Vary rhythm on purpose.** Identical section padding, identical card grids, identical icon-title-blurb triplets from top to bottom is the mark of a template. Vary density, scale, and column structure to reflect content importance.

## 2. Spacing and rhythm

- Use a **4px base** scale with deliberate jumps (`--space-1…9` in tokens): 4, 8, 12, 16, 24, 32, 48, 72, 112. Don't invent 13px or 22px.
- **Inside → outside rule:** padding inside a component ≤ gap between siblings ≤ gap between sections. This produces the "breathing" hierarchy without any lines.
- Controls: horizontal padding ≈ 1.5-2× vertical; consistent heights across all controls (e.g. 32/40/48px) so buttons, inputs, and selects align in a row.
- Vertical rhythm: line-height and block spacing in multiples of a baseline (e.g. 4px / 8px) keeps stacks tidy.
- Prose: `max-width: var(--measure)` (~60-70ch). Wide screens get whitespace or a second column, not longer lines.

## 3. Grid, containers, and breakpoints

- **Page container:** `max-width` ~ 1200-1440px (or full-bleed for tools/dashboards), horizontal padding `clamp(1rem, 4vw, 3rem)`, centered with `margin-inline: auto`.
- **Grid:** 4 columns (phone) → 8 (tablet) → 12 (desktop) is a solid default; use CSS Grid `repeat(auto-fit, minmax(min(100%, 18rem), 1fr))` for fluid card sets instead of stacking media queries.
- **Breakpoints (starting points; move them to where content strains):**

| Name | Approx. width | Typical shift |
|---|---|---|
| base | 320-599 | Single column, bottom/hamburger nav, stacked forms, sticky bottom action bar |
| sm | ≥ 600 | 2-up cards, larger gutters |
| md | ≥ 840-900 | Sidebar appears (collapsed rail or full), 2-column forms where sensible, table shows more columns |
| lg | ≥ 1200 | Full sidebar + content + optional detail pane |
| xl | ≥ 1600 | Cap content width; add supplementary panels rather than stretching |

- **Container queries** for components that live in different-width slots (a card in a sidebar vs. main): `container-type: inline-size` on the wrapper, `@container (min-width: 28rem)` on the component. Components respond to *their* space, not the viewport. Use them for anything reusable.
- Prefer `min-width` (mobile-first) media queries; use `rem`-based breakpoints so user font-size settings scale the layout.

## 4. The placement contract

Decide once per product (record in `DESIGN.md`), then never re-decide per screen.

| Element | Default rule | Rationale |
|---|---|---|
| Page title (`h1`) | Top-left of content area, same offset every page | Orientation anchor |
| Primary page action | Top-right of the page header on desktop; sticky bottom bar or FAB-style bar on mobile | Predictable location; thumb reach |
| Secondary/tertiary actions | Adjacent to primary, visually quieter; overflow menu (`…`) when >2 | Reduce choice overload |
| Filters / search / sort | Row directly above the list/table they affect; collapse into a "Filters" sheet on mobile with an applied-count badge | Cause next to effect |
| Bulk actions | Toolbar appears in place of the filter row when rows are selected | Context switch is obvious |
| Form actions | At the end of the form, left-aligned with the fields; sticky footer for long forms | Follows reading flow |
| Dialog footer | One consistent order (e.g. secondary left, primary right) everywhere | Muscle memory |
| Destructive actions | Separated from primary (space or a "Danger zone" section), never adjacent-and-identical | Prevent accidents |
| Navigation | Persistent, same place across pages; current page marked | Wayfinding |
| Help / support | Same place in shared layout (WCAG 3.2.6) | Findable when stuck |
| Notifications / toasts | One consistent corner (bottom-center or top-right); not covering primary actions on mobile | Predictable |
| User/account menu | Top-right (desktop), inside nav on mobile | Convention |
| Search | Prominent in the header if the product is content-heavy; icon that expands otherwise | Match importance to usage |
| Row-level actions | Far right of row, or overflow menu; keyboard-reachable | Consistent scan path |

**Reading-flow guidance:** people scan in an F/Z-ish pattern on text-heavy pages, but on applications they look where the last interaction happened. Put results, confirmations, and errors near the thing the person just touched.

## 5. Page patterns (with wireframes)

**Shell (app):**
```
≥ md:                                     base (phone):
┌────┬──────────────────────────────┐    ┌──────────────────────┐
│Nav │ Title                [Primary]│    │ ☰  Title      ⋯     │
│    │ ─────────────────────────────│    ├──────────────────────┤
│    │ Filters  ▾  ▾  [Search…]     │    │ [Search…]  [Filters·2]│
│    │ ┌────────────────────────┐   │    │ ┌──────────────────┐ │
│    │ │ content                │   │    │ │ content (cards)  │ │
│    │ └────────────────────────┘   │    │ └──────────────────┘ │
└────┴──────────────────────────────┘    ├──────────────────────┤
                                          │ [   Primary action  ]│ ← sticky
                                          └──────────────────────┘
```
Navigation: sidebar (≥ md) ⇄ bottom tabs (≤ 5 top destinations) or drawer (base). Sidebars can collapse to icon+label rails; never icon-only without labels/tooltips for unfamiliar icons.

**List → detail:**
- Wide: master list on the left, detail on the right (both visible); Narrow: list page → detail page with a real Back link and URL per item.
- Every detail state has its own URL (deep-linkable, shareable, back-button-safe).

**Form page:**
```
Title
Short line about what this is for

Group heading
[Label                     ]      ← single column, label above,
[Input ................... ]        width ≈ expected input
[Label            ][Label   ]      ← side-by-side only for tightly related short fields
                                     (city/postcode), stacks at base
[Primary]  Cancel                  ← actions aligned with fields
```
Single column beats multi-column for completion. Use 2 columns only for tiny related pairs, and never make reading order zigzag.

**Dashboard:** lead with the 1-3 things this person came to check (a status line, a chart with a takeaway sentence), then details. Widget order = importance, not "what was easy to build." Avoid the row of four identical stat cards with a gradient icon; give the *most important* figure more size and context (trend, target, "what changed").

**Settings:** left sub-navigation (≥ md) / list of sections (base); each section is a labelled group; changes save per-section or auto-save with feedback; danger zone last.

**Marketing/landing:** the first screen shows the product or its outcome in the subject's own visual language, not a stock hero with two buttons. Vary section structure; use real content; one CTA repeated, not five different asks.

**Auth screens:** single task, one column, ≤ 400px wide, visible labels, password-manager friendly, clear error messages, "Forgot password" adjacent to the password field, no auto-advancing surprises.

## 6. Responsive transformations, by component

| Component | ≥ md | base |
|---|---|---|
| Sidebar nav | Persistent | Bottom tabs (≤5) or slide-in drawer (`<dialog>`/inert background) |
| Top bar actions | Inline buttons | Primary stays; rest in overflow menu |
| Data table | Full columns, sticky header | Card/list rows showing 2-3 key fields, "Details" reveals rest; or horizontally scrollable with sticky first column when comparison matters |
| Filters | Inline row / left panel | Bottom sheet with "Apply" and count badge |
| Modal dialog | Centered, max-width ~ 32-40rem | Bottom sheet or full-screen; sticky footer with primary action |
| Multi-column form | 2 columns for related pairs | 1 column |
| Tabs | Horizontal tabs | Horizontal scroll with visible overflow affordance, or segmented control / select if many |
| Cards grid | auto-fit columns | 1 column, image ratio preserved |
| Hover-revealed actions | On hover **and** focus | Always visible or in an overflow menu (no hover on touch) |
| Tooltips | Supplemental | Move essential text inline |
| Charts | Full axes and legend | Simplified: fewer ticks, direct labels, or switch to a sparkline + number |
| Wide media | Aspect-ratio boxes | Same, full-bleed edge-to-edge |

Rule: **reflow, don't hide.** If something is important enough for desktop, it needs a home on mobile (even if one tap deeper). If it isn't, it probably shouldn't be on desktop either.

## 7. Touch and thumb reach

- Primary actions in the bottom third on phones (thumb zone): sticky bottom bar, bottom sheets. Destructive or rarely-used actions go to the top/hard-to-reach area or behind a menu.
- Hit targets ≥ 44×44px with ≥ 8px between neighbors; enlarge hit areas invisibly if the visual is smaller.
- Avoid edge gestures that conflict with OS gestures; don't rely on swipe or long-press as the only path.
- Inputs: ≥ 16px font size to prevent iOS zoom-on-focus; correct `inputmode`/`type` to bring the right keyboard; keep the focused field visible above the keyboard (use `scroll-margin`, `interactive-widget` viewport hint, or `dvh` units).
- Sticky bars: account for `env(safe-area-inset-*)` and set `scroll-padding` so focused elements aren't hidden beneath them.

## 8. Robustness: content, overflow, i18n

- Never fix heights on text containers. Use `min-height`, let content grow.
- Long strings: `overflow-wrap: anywhere` (or `word-break`) in flex/grid children with `min-width: 0` (the classic "flex child won't shrink" bug). Truncate deliberately with `text-overflow: ellipsis` and expose the full value.
- Test with: 2-character and 80-character names, no avatar, no data, 10,000 rows, missing optional fields, very large numbers.
- **i18n:** use logical properties (`margin-inline-start`, `padding-block`, `inset-inline-end`, `text-align: start`) so RTL works free; expect German/Finnish +30-40% text length; don't build layouts that only work with English label widths; mirror directional icons (arrows, chevrons) but not logos/media controls.
- Use `text-wrap: balance` for headings and `text-wrap: pretty` for paragraphs to avoid orphans.
- Images: `width`/`height` attributes or `aspect-ratio`, `object-fit`, `loading="lazy"` below the fold, `srcset/sizes`, modern formats. Prevent layout shift.

## 9. Modern CSS toolbox (prefer these to JS and hacks)

- `display: grid` with `grid-template-areas` for page shells; `subgrid` for aligning inner card parts across a row.
- `clamp()` for fluid type and spacing; `min()`/`max()` for widths: `width: min(100% - 2rem, 72rem)`.
- `dvh/svh/lvh` instead of `vh` for full-height mobile layouts.
- `:has()` for parent-state styling (`.field:has(:invalid)`); `:focus-within`, `:where()` for zero-specificity resets.
- `@container`, `@layer` (order: reset, tokens, base, components, utilities), `@property` for animatable tokens, native CSS nesting.
- `position: sticky` headers with matching `scroll-margin-top` on anchor targets.
- `aspect-ratio`, `gap`, `place-items`, `inset`, `accent-color` (native controls take on brand color).
- `<dialog>`, `popover` attribute, and `inert` for overlays where they meet your browser support; feature-detect otherwise.
- `view-transition` / `@starting-style` for meaningful route or state transitions (guard with reduced motion).
- Avoid `!important` and deep selectors; if you need them, the layering is wrong. Avoid `z-index` numbers outside the token scale.

## 10. Test matrix

Check every new screen at: **320, 375, 768, 1024, 1440, 1920** wide, portrait and landscape phone, 200% and 400% zoom, with dev-tools throttling, in light and dark, with long content, and with empty content. Confirm: no horizontal scroll (except deliberate), no overlapped or clipped controls, primary action findable in <2s, thumb-reachable on phone, focus never hidden beneath sticky elements, and DOM order still makes sense with CSS off.
