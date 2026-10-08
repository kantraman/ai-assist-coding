# Color and theming

Color is decision-making under constraints: meaning, contrast, mood, and brand, all at once. The way
to get something distinctive *and* accessible is to derive the palette from the subject, express it
as **roles** (semantic tokens), and verify with numbers.

## Contents
1. Derive the palette from the subject
2. Build with roles, not swatches
3. Why OKLCH
4. Neutrals carry the personality
5. Accent discipline: the 60-30-10 idea, done honestly
6. Semantic colors (success, warning, danger, info)
7. Dark mode is a second design
8. Data visualization palettes
9. Making themes real in code (CSS, Tailwind, Angular Material, Vue, Inertia)
10. Worked directions (to show the range, not to copy)
11. Common failures

---

## 1. Derive the palette from the subject

Before picking a hex, answer in one line each:
- What physical things live in this domain? (paper, glazed tile, brass, canvas, salt, ink, timber, concrete, linen, medicine packaging, signage, maps)
- What is the person's emotional state when using it? (anxious, rushed, celebratory, focused, bored)
- What would competitors all look like? **Avoid that.** Look at the top 3 products in the category and note their palette; then move away from the shared center.
- Where must color *mean* something? (status, risk, priority, category) Reserve those hues; don't spend them on decoration.

Then choose **one brand hue** with a reason you can say out loud ("boatyard: weathered teal + rope-tan", "pharmacy: clinical but not cold, so a green-tinged white with deep ink"). A palette you can justify is a palette that feels designed.

## 2. Build with roles, not swatches

Two layers only (see `assets/tokens.css`):

1. **Primitives / hue inputs**: a handful of numbers (`--h-brand`, `--h-neutral`).
2. **Semantic roles**: what the color *does*: `--bg`, `--surface`, `--surface-sunken`, `--border`, `--border-strong`, `--text`, `--text-muted`, `--brand`, `--on-brand`, `--brand-text`, `--brand-subtle`, `--danger*`, …

Components only ever reference roles. A card never says `blue-500`. It says `--surface` and `--border`. This is what makes dark mode, brand themes (multi-tenant!), and re-skins trivial.

Pairs matter more than colors: every "X-on-Y" pairing you use should be a *tested* pair. Name them (`--on-brand` sits on `--brand`).

Why both `--brand` and `--brand-text`? A color that works as a **fill** under white text (mid lightness) is often too light to work as **text** on a light page. Splitting them lets each be tuned to its own contrast job.

## 3. Why OKLCH

- Perceptually uniform: equal lightness numbers *look* equally light across hues, so a scale built by stepping L behaves predictably. HSL lies (yellow at L50 is far brighter than blue at L50).
- Contrast is mostly a function of L. Fix L for the job (text ≈ 20-30% or 90%+, fills ≈ 45-55%), then choose C and H for character.
- Chroma has gamut limits per hue and lightness. Cyan, yellow, and very light/dark colors run out of headroom fast. `scripts/contrast.py` flags out-of-gamut values so you know when the browser will clip and change the color you "designed."
- Derive states with `color-mix(in oklch, var(--brand), black 12%)` rather than hand-picking a hover hex.
- Provide an sRGB fallback only if you must support very old browsers; OKLCH and `light-dark()` are Baseline in current evergreen browsers.

## 4. Neutrals carry the personality

Pure gray (`#888`, `oklch(x 0 0)`) is what unconsidered interfaces are made of. Neutrals are ~80% of the pixels, so tint them:

- Tint toward the brand hue at very low chroma (0.005-0.02), for cohesion; or
- Tint toward a *complementary or era-specific* warmth/coolness (bone, slate, putty) for a distinctive mood.
- Pure white `#fff` page + pure black `#000` text is harsh; `--surface` can be near-white and `--text` a deep tinted ink. Keep contrast ≥ 7:1 for body text where you can (comfortable, not required).
- Build 3 surface steps (`--bg` < `--surface` < raised) and 2 border steps (decorative vs. ≥3:1 strong). Depth comes from surface steps as much as shadows.

## 5. Accent discipline

- One brand hue does the heavy lifting: primary buttons, links, selected states, focus ring. If everything is accent-colored, nothing is.
- A **secondary** accent is optional; it earns its place only if it carries a separate meaning (e.g. "AI-generated", "internal", "premium").
- Aim for roughly 90% neutral / 8% brand / 2% signal color by area. If a screenshot looks "colorful" the palette is probably too loud for a working tool.
- Gradients: avoid decorative gradient washes. If used, keep them in one hue family, low chroma delta, and never behind text without testing contrast at the worst point.

## 6. Semantic colors

- Keep semantic hues **stable and conventional**: red-ish danger (≈ hue 25-30), amber warning (≈ 70-90), green success (≈ 145-155), blue info (≈ 245-255). People bring habits with them. Adjust chroma/lightness to sit *with* your neutrals, not the hue.
- If the brand hue is close to a semantic hue (a red or green brand), differentiate by lightness/shape/iconography and make the semantic version clearly different from the brand version. Never let "brand red" look like "error red".
- Each semantic color needs: `-text` (on bg), `-subtle` (tinted background), and often a solid fill + `on-` color. Warning text on white almost always needs to be **dark amber/brown**, not the bright yellow you see on the swatch.
- Status is color + icon + word. Always.

## 7. Dark mode is a second design

Inverting is not designing. Rules that keep it good:
- Background isn't pure black unless it's an OLED-first product; start ~L 15-20% with the neutral tint. Raised surfaces get **lighter**, not darker.
- Reduce chroma on large areas; saturated fills vibrate on dark. Text colors shift lighter and slightly less saturated.
- Shadows don't read; use surface lightness steps and subtle 1px borders.
- Brand fill often flips: light-lightness fill (L≈70%) with **dark** `--on-brand`.
- Images/illustrations: add a subtle overlay or provide alternates; white-background logos and screenshots glare.
- Verify both themes with the checker. Contrast bugs hide in the theme you didn't design first.
- Implementation: `color-scheme: light dark` + `light-dark()` per token, `data-theme` attribute to override. Persist the choice, apply it before first paint (inline script in `<head>`) to avoid a flash. Provide three options in settings: System / Light / Dark.

## 8. Data visualization palettes

- Categorical: ≤ 6-7 hues that stay distinguishable for the common color-vision deficiencies; vary **lightness** as well as hue; add direct labels, markers, or dash patterns.
- Sequential: one hue, L ramp (light = low). Diverging: two hues meeting at a neutral midpoint, colorblind-safe pair (blue/orange; avoid red/green as the only pair).
- Reserve semantic red/green for status only, not for "series 1 / series 2".
- Gridlines: `--border`, not black. Axis text at ≥ 4.5:1. Data ink gets the contrast; chrome gets quiet.
- Tools to sanity check: color-blindness simulation in browser dev tools (Rendering → Emulate vision deficiencies).

## 9. Making themes real in code

*Retheming an existing codebase? Follow `redesign-existing.md` §6-7 (tokens with the current values first, then swap them) rather than editing colours in place.*

**Plain CSS / any framework:** tokens as CSS custom properties on `:root` (see `assets/tokens.css`). Components consume `var(--role)`. Framework-agnostic and works for React, Vue, Angular, Inertia alike.

**Tailwind v4:** map roles in `@theme` so utilities exist for them and dark mode comes from the variables:
```css
@import "tailwindcss";
@theme inline {
  --color-bg: var(--bg);
  --color-surface: var(--surface);
  --color-text: var(--text);
  --color-brand: var(--brand);
  --color-on-brand: var(--on-brand);
}
/* then: class="bg-surface text-text border-[--border-strong]" */
```
Delete the default palette from use in components (`bg-blue-500` in markup = no theming, no consistency). With Tailwind v3, expose the same names via `theme.extend.colors` pointing at `var(--role)` (use `oklch(from ...)`/`<alpha-value>` patterns if opacity modifiers are needed).

**Angular Material (M3):** theme with the Material 3 theming API and override via its system tokens (CSS custom properties, `--mat-sys-*` in current versions), then bridge your roles to them, so your own components and Material components share one source of truth. Check the version's docs; the API has changed between releases.

**Vue / Nuxt UI, Reka UI, PrimeVue etc.:** these expose CSS variables or design-token presets; point them at your roles instead of re-declaring colors. In SFCs, `v-bind()` in `<style>` is fine for dynamic values, but static theme values belong in tokens.

**Inertia (Laravel):** tokens live in your CSS entry (Vite) and are framework-agnostic. Persist theme preference in a cookie so the server can render `data-theme` on first response, and there's no flash. Share it via Inertia shared props only if the UI needs to read it.

**Multi-tenant / white-label:** tenants supply *hue + a few lightness knobs*, not raw hex for every role. Generate roles from those inputs and run the contrast check at runtime or build-time; reject/adjust combos that fail. Never let a tenant color produce unreadable text.

## 10. Worked directions (illustrative reasoning, not palettes to copy)

- **Community clinic booking:** subject cues: paper forms, sage-painted walls, ink stamps. Neutrals: warm putty (`h-neutral` ≈ 85, very low chroma). Brand: deep sage-teal (≈ 175-185) at modest chroma; signature: an ink-stamp style confirmation. Feels calm, human, not "medical blue."
- **Freight-tracking dashboard for dispatchers:** cues: hi-vis, safety signage, night shifts. Dark-first, cool graphite neutrals, brand: signal amber used **only** for "needs attention"; the rest stays quiet so amber means something. Dense, tabular, numeric-forward.
- **Indie bookshop storefront:** cues: kraft paper, cloth bindings, ink. Neutrals: off-white with a slight yellow-green cast; brand: oxblood or deep petrol; type does most of the branding.
- **Internal finance tool:** cues: ledgers, green-shade lamps. Restraint: near-monochrome neutrals + one calm blue-green; color reserved for variance (over/under budget) using a colorblind-safe diverging pair.

Notice each starts from a *place and a feeling*, not from "modern SaaS."

## 11. Common failures (check before shipping)

- Purple→blue gradient hero and a lavender/indigo primary because it's "the default AI look." Only if the subject truly calls for it.
- Muted text at 3:1 "because it looks elegant." Placeholder text and secondary labels are the top WCAG failures. Floor at 4.5:1.
- Brand color used for fill *and* small text without a separate text role.
- Semantic color used decoratively (green for "Sign up" then green for "Success"; red for a logo then red for "Error").
- Hover state that lowers contrast below the rest state.
- Focus ring matching the button fill so it disappears when focused.
- Three near-identical grays with no rule for which does what.
- Dark mode made by `filter: invert(1)`.
- Colors specified as raw hex scattered through components.
- Trusting screenshots on one calibrated monitor; test on a phone outdoors-brightness and on a cheap laptop panel.
