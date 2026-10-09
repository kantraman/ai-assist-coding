---
name: web-graphics-studio
description: Build striking graphics, animations, interactive visuals and attractive web pages using modern web technologies (HTML5, CSS3, SVG, Canvas 2D, WebGL/three.js, GSAP, Web Animations API, scroll-driven animation). Use this skill whenever the user wants a landing page, portfolio, hero section, animated background, generative art, particle effect, data visualization, logo animation, loader, micro-interaction, 3D scene, scroll storytelling, animated infographic, or says "make it look good", "beautiful", "modern", "animated", "eye-catching" or "wow" about anything that runs in a browser. Use it even if the user does not name a technology; if the output is something people will look at in a browser, consult this skill.
---

# Web Graphics Studio

Create visuals that look designed rather than generated: a clear concept, a disciplined palette, purposeful motion, and code that runs smoothly on a phone.

## Workflow

1. **Pick a concept before writing code.** Write one sentence: the subject, the mood, and the single memorable thing (a hero animation, a signature color, a distinctive typeface pairing). A page with one confident idea beats ten effects.
2. **Choose the lightest technology that achieves it** (table below). Heavier tools cost load time, battery and fragility.
3. **Set design tokens first** (colors, type scale, spacing, radii, easing, durations) as CSS custom properties. Everything else references them, which keeps the result coherent and makes light/dark themes trivial.
4. **Build structure and static layout first, then add motion.** If the static page is not attractive, animation will not rescue it.
5. **Add motion with intent, then add the safety nets**: `prefers-reduced-motion`, pausing offscreen work, responsive sizing, and a fallback if a library fails to load.
6. **Check the checklist at the bottom** before delivering.

For file creation and delivery rules (where to save, publishing as an artifact vs. presenting a file), follow the environment's own instructions. If the `frontend-design` skill is available and the task is a full UI or app, read it too; this skill focuses on visuals and motion.

## Choosing the technology

| Need | Use | Why |
|---|---|---|
| Fade, slide, hover, simple loops | CSS transitions/keyframes | Zero JS, GPU-friendly |
| Scroll-linked reveals and parallax | CSS `animation-timeline: view()` / `scroll()` with an IntersectionObserver fallback | No scroll listeners, smooth |
| Sequenced, choreographed timelines | GSAP (+ ScrollTrigger) or Web Animations API | Precise control, easing, scrubbing |
| Icons, logos, diagrams, line drawing, morphing | Inline SVG (+ CSS/GSAP) | Crisp at any size, stylable |
| Particles, generative art, fluid backgrounds, thousands of moving things | Canvas 2D | Fast pixel-level control |
| 3D, shaders, heavy GPU effects | three.js or raw WebGL fragment shader | Only when 3D/shaders are the point |
| Charts and data visuals | Inline SVG or Canvas (D3 for scales/layout if needed) | Accessible, exact |

Default order of preference: CSS → SVG → Canvas 2D → WebGL. Escalate only when the lighter option cannot do the job.

## Design principles

- **Color**: one dominant hue, one accent, neutrals with a slight tint of the dominant hue. Use `oklch()` or HSL so you can derive shades systematically. Check contrast (text ≥ 4.5:1). Gradients should shift hue slightly, not jump across the wheel.
- **Typography**: two families at most. Pair a characterful display face with a neutral text face, or use one variable font with expressive weights. Use `clamp()` for fluid sizes, tight tracking on large headlines, generous line-height (1.5–1.7) on body text. Load Google Fonts when allowed, always with a real fallback stack (`system-ui, sans-serif`).
- **Layout**: CSS Grid for page structure, Flexbox for components. Use an 8px rhythm, generous whitespace, and a max content width (60–75ch for reading, ~1200px for layouts). Break the grid deliberately in one place for emphasis.
- **Depth**: layered soft shadows, subtle borders (`1px` at low alpha), glass effects via `backdrop-filter` used sparingly, grain/noise overlays for texture (inline SVG `feTurbulence`).
- **Avoid the generic look**: no default purple-on-white gradient hero, no stock three-card grid with emoji icons unless the brief calls for it. Make a specific choice that fits the subject.

## Motion principles

- **Purpose**: motion should guide attention, show causality, or add delight. Remove it if it does none of these.
- **Timing**: micro-interactions 120–250ms; entrances 400–800ms; ambient loops 6–20s. Stagger siblings by 40–90ms.
- **Easing**: never `linear` for UI movement. Use `cubic-bezier(.22,1,.36,1)` (ease-out-expo feel) for entrances, `cubic-bezier(.65,0,.35,1)` for in-out. Springs feel alive for drag/hover.
- **Performance**: animate only `transform` and `opacity` where possible. Avoid animating `width`, `height`, `top`, `left`, large `box-shadow` or `filter: blur` on big areas. Use `will-change` sparingly and only on elements about to animate.
- **Respect users**: wrap non-essential motion in `@media (prefers-reduced-motion: no-preference)`, or reduce to simple fades.
- **Pause what is not visible**: use IntersectionObserver to stop canvas/WebGL loops offscreen and `document.hidden` to pause in background tabs.

## Implementation rules

- **Single self-contained HTML file** unless asked otherwise: inline CSS and JS, SVG inline, images as data URIs. This is also what hosted/published pages require.
- **External libraries**: when the environment restricts hosts, load only from allowed CDNs (commonly `cdnjs.cloudflare.com` and `cdn.jsdelivr.net/npm/`), pinned to an exact version, as a plain `<script>` UMD build. Prefer no library when 40 lines of vanilla JS will do. Always guard: `if (window.gsap) {...} else {show static state}`.
- **No browser-storage or network assumptions** in demos; keep state in memory. Wrap any storage use in try/catch.
- **Responsive**: `<meta name="viewport" content="width=device-width, initial-scale=1">`, relative units, `min()/max()/clamp()`, container queries for components. Test mentally at 375px and 1440px.
- **Canvas**: size to `devicePixelRatio` (capped at 2), handle `resize`, use `requestAnimationFrame` with delta time, never `setInterval`.
- **Accessibility**: semantic landmarks (`header/main/section/footer`), one `h1`, alt text or `aria-hidden="true"` on decorative graphics, visible `:focus-visible` styles, keyboard-reachable controls, `<canvas>` gets an `aria-label` or fallback text.
- **Theme-aware**: define color tokens on `:root` and override under `@media (prefers-color-scheme: dark)`.

## Reference files (read only what the task needs)

- `references/css-recipes.md`: tokens, fluid type, gradients, glassmorphism, grain, marquee, scroll-driven animation, view transitions, bento grid, hover effects.
- `references/svg-and-canvas.md`: SVG line-draw, morphing, filters, masks; Canvas particle system, flow field, noise, gradient mesh, resize/DPR handling.
- `references/animation-libraries.md`: GSAP timelines and ScrollTrigger, Web Animations API, three.js starter, fragment-shader background, easing cheat sheet.
- `references/page-patterns.md`: section blueprints (hero, features, pricing, portfolio, case study, footer), copywriting tips, and three complete style directions to draw from.
- `assets/starter.html`: a polished starter page with tokens, theme support, reveal-on-scroll, animated canvas hero and reduced-motion handling. Copy and adapt it rather than starting from a blank file when building a page.

## Quality checklist

- [ ] There is one clear concept and one memorable moment.
- [ ] Palette, type and spacing come from tokens; no stray hard-coded values.
- [ ] Works at phone and desktop widths with no horizontal page scroll.
- [ ] Text contrast passes in light and dark.
- [ ] `prefers-reduced-motion` handled; loops pause offscreen.
- [ ] Only `transform`/`opacity` animated on hot paths; canvas uses DPR cap and rAF.
- [ ] Page still reads well if JS or a CDN library fails.
- [ ] Decorative graphics hidden from assistive tech; interactive elements keyboard accessible.
- [ ] No console errors; external scripts pinned and from allowed hosts only.

## Response style

When delivering, state in one or two sentences the concept, the main technologies used, and any assumption you made. Offer one or two concrete directions for iteration (for example a different palette mood or a 3D variant) rather than a long explanation.
