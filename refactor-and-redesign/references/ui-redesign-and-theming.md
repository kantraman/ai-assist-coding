# UI Redesign and Theming

Contents: 1. Order of work, 2. UI audit, 3. Design tokens, 4. Building a palette,
5. Dark mode, 6. Type, spacing, shape, 7. Migrating hardcoded styles, 8. Framework mapping,
9. Visual verification checklist, 10. Avoiding generic results.

## 1. Order of work

Always go in this order. Doing pages before tokens means redoing the pages.

1. Audit what exists.
2. Define tokens (colors, type, spacing, radius, shadow) in ONE place.
3. Restyle primitives (button, input, card, link, badge) using tokens only.
4. Restyle composed components and layouts.
5. Restyle pages.
6. Add theme variants (dark mode, brand variants) by changing token values only.
7. Cleanup: delete unused styles and leftover hardcoded values.

## 2. UI audit

Run `python scripts/find_hardcoded_colors.py <dir>` and record the count in `PLAN.md`. Then list:
- The distinct colors, font sizes, spacings, and radii actually in use (expect many near-duplicates like `#333`, `#343434`, `#323232`).
- Components that exist in several slightly different versions (three kinds of button).
- Where styles live (global CSS, CSS modules, utility classes, inline styles, theme objects).
- Any existing theme mechanism. Extend it instead of adding a second one.

Group near-duplicates into the smallest set that covers the real needs. That set becomes the tokens.

## 3. Design tokens: three layers

1. **Primitive tokens**: raw values, no meaning. `blue-500: #3b82f6`, `space-4: 16px`.
2. **Semantic tokens**: meaning, point to primitives. `color-bg`, `color-surface`, `color-text`,
   `color-text-muted`, `color-border`, `color-primary`, `color-primary-hover`, `color-danger`, `color-focus-ring`.
3. **Component tokens** (only when needed): `button-bg`, `input-border`, point to semantic tokens.

Rules:
- Components use semantic or component tokens only, never primitives or raw values.
  This is what makes theme switching a data change instead of a code change.
- Name by role, not by appearance. `color-danger` yes, `color-red` no, so the value can change.
- Minimum semantic set: bg, surface, surface-raised, text, text-muted, border, primary, on-primary,
  success, warning, danger, focus-ring. Add more only when a real need appears.

## 4. Building a palette

Inputs: brand color(s) or mood words from the user. If none, pick defaults and state them.

Steps:
1. Pick one **primary** hue. Build a 9 to 11 step scale (lightest to darkest) by varying lightness
   in even steps and slightly reducing saturation at the extremes.
2. Pick **neutrals** (gray scale) tinted slightly toward the primary hue. Pure gray feels flat.
3. Pick status colors: success (green), warning (amber), danger (red), info (blue). Keep their lightness
   similar to each other so they feel like one family.
4. Map to semantic tokens for light mode.
5. **Check contrast with the script for every text/background pair.** Run
   `python scripts/contrast.py "#111827" "#ffffff"`. Required minimums (WCAG AA):
   - Normal text: 4.5 : 1
   - Large text (24px, or 19px bold) and UI parts like borders of inputs, icons: 3 : 1
   - Do not rely on color alone to show state (add icon, text, or underline).
6. Check `on-primary` (text on primary buttons) separately. White on a mid-tone primary often fails.

Use about 60% neutrals, 30% secondary surfaces, 10% accent. An interface where everything is
the accent color has no hierarchy.

## 5. Dark mode

Dark mode is a second set of values for the same semantic tokens, not a separate stylesheet.

- Do not invert colors. Rebuild: bg is a very dark neutral (not pure black), surfaces get *lighter*
  as they rise (raised = lighter), text is off-white (not pure white).
- Lower saturation of bright colors a little; saturated colors vibrate on dark backgrounds.
- Shadows barely show on dark; show elevation with lighter surface color and a subtle border.
- Re-run the contrast script on every pair in dark mode. Passing in light mode says nothing about dark mode.
- Respect the system preference by default (`prefers-color-scheme` or the platform equivalent) and let the
  user override. Store the override.
- Images/logos: check them on both backgrounds. Provide alternate assets when needed.

## 6. Type, spacing, shape

- **Type scale**: pick a ratio (1.125 to 1.25) and define 6 to 8 sizes (xs, sm, base, lg, xl, 2xl, 3xl).
  Body at least 16px on web. Line height about 1.5 for body, 1.2 to 1.3 for headings.
  Use at most 2 font families, and a limited set of weights.
- **Spacing scale**: multiples of 4 (4, 8, 12, 16, 24, 32, 48, 64). Use only these values.
- **Radius and shadow**: define 3 radii (sm, md, lg) and 2 to 3 elevations. Apply consistently by component type.
- **Layout**: pick a max content width, a grid or consistent gutters, and one breakpoint set. Design mobile first.
- **Touch targets**: at least 44 x 44 px for tappable things.

## 7. Migrating hardcoded styles

Do this per batch (one component or one folder at a time):
1. Run the color scan on that folder.
2. For each literal, map it to the nearest semantic token. If nothing fits, ask whether a new token is needed.
   Do not add a token for a one-off.
3. Replace the literal with the token reference.
4. Check the result looks the same (or intentionally different if this is a redesign batch).
5. Re-run the scan; the count for that folder should reach 0, except in the token file itself.

Also look for colors in places the scan may miss: named colors (`white`, `red`), image assets, SVG fills,
chart libraries, third-party component themes, email templates, and native platform theme files.

## 8. Framework mapping

The concepts are the same everywhere; only the place you write them changes. Use what the project already has.

| Framework / platform | Where tokens live | Theme switch |
|---|---|---|
| Plain CSS / any web | CSS custom properties on `:root` | `[data-theme="dark"]` or `prefers-color-scheme` overrides the same variable names |
| Tailwind | `theme.extend.colors` mapping to CSS variables (`primary: 'var(--color-primary)'`) | Variables change, class names do not |
| CSS-in-JS (styled-components, emotion) | Theme object + ThemeProvider | Swap the theme object |
| Sass/SCSS | Variables for build-time, CSS custom properties for runtime theming | Use CSS custom properties for anything that must switch at runtime |
| React / Vue / Svelte / Angular | Same as the styling system above; wrap theme choice in one provider/store/service | One toggle, one source of truth |
| Flutter | `ThemeData` + `ColorScheme`, extra tokens via `ThemeExtension` | `themeMode` and `darkTheme` |
| SwiftUI / iOS | Asset catalog color sets with light/dark values, or a `Theme` struct in the environment | Automatic via color sets |
| Android (Compose / XML) | `MaterialTheme` colorScheme, or `values/` and `values-night/` resources | `-night` resources or `isSystemInDarkTheme()` |
| React Native | A theme object in context | Context value swap |

## 9. Visual verification checklist

After each UI batch, check (or ask the user to check) the following. Tick them in `PLAN.md`.

- [ ] Text contrast passes for all pairs touched (script output recorded).
- [ ] Keyboard focus is clearly visible on every interactive element.
- [ ] Hover, active, disabled, and error states all exist and look intentional.
- [ ] Layout works at narrow (about 360px), medium (about 768px), and wide (about 1280px+) widths.
- [ ] No horizontal scrolling on mobile; no overlapping or clipped text; long text wraps sensibly.
- [ ] Both light and dark themes checked, if both are in scope.
- [ ] Empty, loading, and error states are styled, not just the happy path.
- [ ] No leftover hardcoded colors in files touched in this batch.

If you cannot render the UI yourself, say so, and give the user the exact pages/states to look at.

## 10. Avoiding generic results

When the user wants a redesign, not just a recolor, do not fall back to the default look
(white card, blue button, gray text, rounded corners everywhere). Decide on one clear direction
and state it in the plan in one sentence, for example "calm editorial: serif headings, warm neutrals, one terracotta accent, generous space".
Then make every choice (type, color, spacing, shape) serve that sentence. Offer the user two or three
directions to choose from if the brief is open. Keep function and information hierarchy intact; change presentation.
