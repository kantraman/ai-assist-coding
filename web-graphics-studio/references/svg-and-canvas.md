# SVG and Canvas

Contents: SVG basics · line drawing · morphing · filters · masks · Canvas setup · particles · flow field · gradient blobs · performance

## SVG

Use inline SVG with `viewBox` and no fixed width/height so it scales. Style it with CSS variables (`fill: var(--accent)`).

### Line drawing animation

```html
<svg viewBox="0 0 200 100" role="img" aria-label="Wave"><path class="draw" d="M0 50 C 40 0, 60 100, 100 50 S 160 0, 200 50" fill="none" stroke="var(--accent)" stroke-width="3" stroke-linecap="round" pathLength="1"/></svg>
```
```css
.draw { stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 2s var(--ease-out) forwards; }
@keyframes draw { to { stroke-dashoffset: 0; } }
```
`pathLength="1"` normalizes any path so dash math is trivial.

### Morphing between shapes
Paths animate smoothly with CSS `d: path(...)` in Chromium, or with GSAP MorphSVG alternatives. Portable approach: keep the same number and type of commands in both paths and interpolate numbers in JS:

```js
const lerp = (a, b, t) => a + (b - a) * t;
function morph(from, to, t) { return from.map((v, i) => lerp(v, to[i], t)); }
// from/to are arrays of numbers used to build the "d" string each frame
```

### Filters
- Soft glow: `<filter id="glow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>`
- Goo effect (blobs that merge): blur then `feColorMatrix values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 20 -9"`.
- Texture: `feTurbulence` + `feDisplacementMap` makes hand-drawn wobble; animate `baseFrequency` slowly.

Filters are expensive on large animated areas; apply them to small groups or static layers.

### Masks and clips
Use `<clipPath>` for hard edges and `<mask>` with gradients for soft fades. Animate the mask's inner shape's `transform` for reveals.

### Motion along a path
CSS: `offset-path: path("M..."); animation: go 6s linear infinite; @keyframes go { to { offset-distance: 100%; } }`.

## Canvas 2D

### Setup with devicePixelRatio, resize and visibility handling

```js
const canvas = document.querySelector("canvas");
const ctx = canvas.getContext("2d");
let w, h, dpr, running = true, last = 0;

function resize() {
  dpr = Math.min(window.devicePixelRatio || 1, 2);
  w = canvas.clientWidth; h = canvas.clientHeight;
  canvas.width = w * dpr; canvas.height = h * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
new ResizeObserver(resize).observe(canvas); resize();

new IntersectionObserver(([e]) => { running = e.isIntersecting; if (running) requestAnimationFrame(frame); }).observe(canvas);

function frame(t) {
  if (!running) return;
  const dt = Math.min((t - last) / 1000, 0.05); last = t;
  update(dt); draw();
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
```
CSS: `canvas { display:block; width:100%; height:100%; }` and give the parent an explicit height.

### Particle network (connecting lines)

```js
const N = Math.min(120, Math.floor(innerWidth / 12));
const ps = Array.from({ length: N }, () => ({ x: Math.random() * w, y: Math.random() * h, vx: (Math.random() - .5) * 30, vy: (Math.random() - .5) * 30 }));
function update(dt) { for (const p of ps) { p.x += p.vx * dt; p.y += p.vy * dt; if (p.x < 0 || p.x > w) p.vx *= -1; if (p.y < 0 || p.y > h) p.vy *= -1; } }
function draw() {
  ctx.clearRect(0, 0, w, h);
  const accent = getComputedStyle(document.documentElement).getPropertyValue("--accent-rgb") || "120,100,255";
  for (let i = 0; i < ps.length; i++) {
    const a = ps[i];
    ctx.fillStyle = `rgba(${accent},.9)`; ctx.beginPath(); ctx.arc(a.x, a.y, 1.8, 0, 6.283); ctx.fill();
    for (let j = i + 1; j < ps.length; j++) {
      const b = ps[j], d = Math.hypot(a.x - b.x, a.y - b.y);
      if (d < 120) { ctx.strokeStyle = `rgba(${accent},${(1 - d / 120) * .35})`; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke(); }
    }
  }
}
```
The pair loop is O(n²); keep N under ~150 or use a spatial grid.

### Flow field (generative strokes)
Use a smooth noise function (simplex/value noise, ~30 lines inline) to get an angle `a = noise(x*s, y*s, time) * TAU * 2`. Move each particle by `(cos a, sin a) * speed`, draw short semi-transparent lines, and fade the frame with `ctx.fillStyle = "rgba(bg,0.06)"; ctx.fillRect(0,0,w,h)` instead of clearing. This gives trails. Reset particles that leave the screen.

### Soft gradient blobs (cheap "aurora" background)
Draw 3–5 large circles with `createRadialGradient` from `rgba(color, .6)` to `rgba(color, 0)`, moving on slow sine paths (`x = cx + sin(t*0.2+i)*r`). Use `globalCompositeOperation = "lighter"` for glowing overlaps. Render at half resolution and scale up with CSS for a big performance win since the content is blurry anyway.

### Pointer interaction
Track `pointermove` on the container (use `getBoundingClientRect` for coordinates). Apply a repulsion or attraction force to particles within a radius. Ease the pointer position toward the target (`p += (target - p) * 0.1`) so motion feels smooth.

## Performance tips
- Batch draw calls: one `beginPath()` with many `moveTo/lineTo`, then a single `stroke()`.
- Avoid `shadowBlur` and `filter` on the 2D context in hot loops.
- Pre-render static or repeated shapes to an offscreen canvas and `drawImage` it.
- Use `Float32Array` for large particle sets; avoid allocating objects inside the frame loop.
- Cap frame work on mobile: lower particle count when `innerWidth < 640`.
- Provide a static fallback (a drawn gradient) when `prefers-reduced-motion: reduce`; render one frame and do not loop.
