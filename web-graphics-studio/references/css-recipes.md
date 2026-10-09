# CSS Recipes

Contents: tokens · fluid type · gradients · glass · grain · marquee · scroll-driven · view transitions · bento grid · hover effects · reduced motion

## Design tokens

```css
:root {
  --hue: 265;
  --bg: oklch(98% 0.01 var(--hue));
  --surface: oklch(100% 0 0);
  --text: oklch(22% 0.03 var(--hue));
  --muted: oklch(50% 0.03 var(--hue));
  --accent: oklch(65% 0.22 calc(var(--hue) + 40));
  --border: oklch(22% 0.03 var(--hue) / .12);
  --radius: 16px;
  --ease-out: cubic-bezier(.22, 1, .36, 1);
  --ease-in-out: cubic-bezier(.65, 0, .35, 1);
  --shadow: 0 1px 2px #0001, 0 8px 24px -8px #0002, 0 24px 48px -24px #0002;
  --font-display: "Space Grotesk", system-ui, sans-serif;
  --font-body: "Inter", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: oklch(16% 0.02 var(--hue));
    --surface: oklch(21% 0.025 var(--hue));
    --text: oklch(95% 0.01 var(--hue));
    --muted: oklch(70% 0.02 var(--hue));
    --border: oklch(95% 0.01 var(--hue) / .12);
  }
}
html { background: var(--bg); color: var(--text); font-family: var(--font-body); }
```

`oklch()` has wide support; if you must support very old browsers, provide an HSL fallback line first.

## Fluid typography

```css
h1 { font-size: clamp(2.5rem, 1.5rem + 5vw, 6rem); line-height: 1.02; letter-spacing: -0.03em; text-wrap: balance; }
p  { font-size: clamp(1rem, .95rem + .25vw, 1.15rem); line-height: 1.65; max-width: 65ch; text-wrap: pretty; }
```

## Gradients

```css
/* Gradient text */
.gradient-text { background: linear-gradient(100deg, var(--text), var(--accent)); -webkit-background-clip: text; background-clip: text; color: transparent; }

/* Mesh-like background from stacked radial gradients */
.mesh {
  background:
    radial-gradient(at 20% 10%, oklch(75% .18 var(--hue) / .55), transparent 50%),
    radial-gradient(at 80% 0%,  oklch(75% .18 calc(var(--hue) + 60) / .45), transparent 50%),
    radial-gradient(at 50% 100%, oklch(70% .2 calc(var(--hue) - 50) / .4), transparent 55%),
    var(--bg);
}

/* Animated gradient border */
@property --angle { syntax: "<angle>"; inherits: false; initial-value: 0deg; }
.glow-border { border: 2px solid transparent; border-radius: var(--radius);
  background: linear-gradient(var(--surface), var(--surface)) padding-box,
              conic-gradient(from var(--angle), var(--accent), transparent 30%, var(--accent)) border-box;
  animation: spin 6s linear infinite; }
@keyframes spin { to { --angle: 360deg; } }
```

## Glassmorphism (use sparingly, over a colorful background)

```css
.glass { background: oklch(100% 0 0 / .08); backdrop-filter: blur(16px) saturate(140%); border: 1px solid oklch(100% 0 0 / .18); border-radius: var(--radius); box-shadow: var(--shadow); }
```

## Grain overlay (inline SVG noise, no image file)

```css
body::after { content: ""; position: fixed; inset: 0; pointer-events: none; opacity: .06; mix-blend-mode: overlay; z-index: 50;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>"); }
```

## Infinite marquee

```html
<div class="marquee"><div class="track"><span>Design</span><span>Motion</span><span>Code</span><!-- duplicate the set once --><span>Design</span><span>Motion</span><span>Code</span></div></div>
```
```css
.marquee { overflow: hidden; mask-image: linear-gradient(90deg, transparent, #000 10%, #000 90%, transparent); }
.track { display: flex; gap: 3rem; width: max-content; animation: scroll 24s linear infinite; }
.marquee:hover .track { animation-play-state: paused; }
@keyframes scroll { to { transform: translateX(-50%); } }
```

## Scroll-driven animation (native) with fallback

```css
@keyframes rise { from { opacity: 0; transform: translateY(32px); } to { opacity: 1; transform: none; } }
@supports (animation-timeline: view()) {
  .reveal { animation: rise linear both; animation-timeline: view(); animation-range: entry 0% cover 30%; }
}
/* Reading progress bar */
@supports (animation-timeline: scroll()) {
  .progress { position: fixed; top: 0; left: 0; height: 3px; width: 100%; background: var(--accent); transform-origin: 0 50%; animation: grow linear both; animation-timeline: scroll(root); }
  @keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
}
```
Fallback for browsers without support: IntersectionObserver adds `.in` class (see `assets/starter.html`).

## View Transitions (same-page state changes)

```js
function swap(update) { document.startViewTransition ? document.startViewTransition(update) : update(); }
```
```css
::view-transition-old(root), ::view-transition-new(root) { animation-duration: .45s; }
.card { view-transition-name: hero-card; } /* names must be unique at a time */
```

## Bento grid

```css
.bento { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); grid-auto-rows: 180px; }
.bento > .wide { grid-column: span 2; } .bento > .tall { grid-row: span 2; }
.bento > * { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; overflow: hidden; }
```

## Hover and interaction effects

```css
/* Lift + glow */
.card { transition: transform .35s var(--ease-out), box-shadow .35s var(--ease-out); }
.card:hover { transform: translateY(-6px); box-shadow: var(--shadow), 0 0 0 1px var(--accent); }

/* Underline sweep */
.link { background: linear-gradient(currentColor, currentColor) 0 100% / 0 2px no-repeat; transition: background-size .4s var(--ease-out); }
.link:hover, .link:focus-visible { background-size: 100% 2px; }

/* Spotlight following the pointer: set --x/--y from JS pointermove */
.spot { background: radial-gradient(240px circle at var(--x, 50%) var(--y, 50%), oklch(100% 0 0 / .12), transparent 60%), var(--surface); }

/* Magnetic/tilt: set transform from JS using pointermove, reset on pointerleave */
```

## Reduced motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; scroll-behavior: auto !important; }
}
```
