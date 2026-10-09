# Animation Libraries and 3D

Contents: loading libraries safely · Web Animations API · GSAP · ScrollTrigger · three.js starter · fragment shader background · easing cheat sheet

## Loading libraries safely

Check which script hosts the environment allows (commonly `cdnjs.cloudflare.com` and `cdn.jsdelivr.net/npm/`). Pin an exact version of the UMD build, place the tag before your inline script, and guard usage so the page still works without it.

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
```
Pick versions you know exist and are not brand new. Never use `@latest`.

## Web Animations API (no library)

```js
const el = document.querySelector(".card");
const anim = el.animate(
  [{ opacity: 0, transform: "translateY(24px) scale(.98)" }, { opacity: 1, transform: "none" }],
  { duration: 700, easing: "cubic-bezier(.22,1,.36,1)", fill: "both", delay: 80 }
);
// anim.pause(), anim.reverse(), anim.finished.then(...), anim.currentTime = ms (scrub)
```
Stagger a list: `items.forEach((el, i) => el.animate(keyframes, { ...opts, delay: i * 70 }))`.

## GSAP

```js
if (window.gsap && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
  const tl = gsap.timeline({ defaults: { ease: "power3.out", duration: 0.9 } });
  tl.from(".hero h1 .word", { yPercent: 110, opacity: 0, stagger: 0.06 })
    .from(".hero p", { y: 20, opacity: 0 }, "-=0.5")
    .from(".hero .cta", { scale: 0.9, opacity: 0 }, "-=0.6");
}
```
Tips:
- Split headline text into `<span class="word">` (wrap each in an `overflow:hidden` parent) for a masked slide-up reveal.
- Use `gsap.quickTo(el, "x", { duration: .4, ease: "power3" })` for pointer-following elements.
- `gsap.matchMedia()` lets you run different animations per breakpoint and for reduced motion.

### ScrollTrigger

```js
gsap.registerPlugin(ScrollTrigger);
gsap.utils.toArray(".reveal").forEach(el =>
  gsap.from(el, { y: 40, opacity: 0, duration: 0.8, ease: "power3.out", scrollTrigger: { trigger: el, start: "top 85%" } }));

// Pinned scrub storytelling
gsap.timeline({ scrollTrigger: { trigger: ".story", start: "top top", end: "+=300%", scrub: 0.6, pin: true } })
  .to(".layer-1", { yPercent: -40 }, 0)
  .to(".layer-2", { scale: 1.3, opacity: 0 }, 0.3)
  .from(".chapter-2", { opacity: 0, y: 60 }, 0.5);
```
Call `ScrollTrigger.refresh()` after fonts or images change layout.

## three.js starter (rotating, lit, responsive)

Keep 3D purposeful: a hero object, a product viewer, an abstract background. Use r128-compatible APIs when loading `three.min.js` from cdnjs (no `OrbitControls` or `CapsuleGeometry` in that build; build gentle pointer-driven rotation yourself).

```js
const canvas = document.querySelector("#scene");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100); camera.position.z = 5;

const mesh = new THREE.Mesh(
  new THREE.IcosahedronGeometry(1.4, 1),
  new THREE.MeshStandardMaterial({ color: 0x7c6cff, roughness: 0.25, metalness: 0.6, flatShading: true })
);
scene.add(mesh);
scene.add(new THREE.AmbientLight(0xffffff, 0.4));
const key = new THREE.DirectionalLight(0xffffff, 1.2); key.position.set(3, 4, 5); scene.add(key);

function resize() {
  const { clientWidth: w, clientHeight: h } = canvas;
  renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(canvas); resize();

const target = { x: 0, y: 0 };
addEventListener("pointermove", e => { target.x = (e.clientY / innerHeight - .5) * .6; target.y = (e.clientX / innerWidth - .5) * .9; });
const clock = new THREE.Clock(); let visible = true;
new IntersectionObserver(([e]) => visible = e.isIntersecting).observe(canvas);
renderer.setAnimationLoop(() => {
  if (!visible) return;
  const t = clock.getElapsedTime();
  mesh.rotation.x += (target.x + Math.sin(t * .4) * .1 - mesh.rotation.x) * .05;
  mesh.rotation.y += (target.y + t * .15 - mesh.rotation.y) * .05;
  renderer.render(scene, camera);
});
```
Clean up geometries, materials and textures (`dispose()`) if objects are removed. Fall back to a static gradient if `WebGLRenderingContext` is unavailable.

## Fragment shader background (raw WebGL, no library)

A full-screen quad with a fragment shader gives flowing, premium-looking gradients with very little code.

```js
const gl = canvas.getContext("webgl");
const vs = `attribute vec2 p; void main(){ gl_Position = vec4(p,0.,1.); }`;
const fs = `precision mediump float; uniform vec2 r; uniform float t;
void main(){
  vec2 uv = gl_FragCoord.xy / r; vec2 q = uv * 2. - 1.; q.x *= r.x / r.y;
  float v = sin(q.x*3.+t) + sin(q.y*4.-t*.8) + sin((q.x+q.y)*2.+t*.5);
  vec3 a = vec3(.10,.08,.35), b = vec3(.55,.35,1.), c = vec3(.1,.8,.9);
  vec3 col = mix(a, b, .5+.5*sin(v)); col = mix(col, c, smoothstep(.6,1.,.5+.5*sin(v*1.7+1.)));
  gl_FragColor = vec4(col, 1.);
}`;
function sh(type, src) { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); return s; }
const prog = gl.createProgram(); gl.attachShader(prog, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(prog); gl.useProgram(prog);
gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
const loc = gl.getAttribLocation(prog, "p"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
const uR = gl.getUniformLocation(prog, "r"), uT = gl.getUniformLocation(prog, "t");
function loop(ms) {
  canvas.width = canvas.clientWidth * .75; canvas.height = canvas.clientHeight * .75; // render lower-res, scale with CSS
  gl.viewport(0, 0, canvas.width, canvas.height); gl.uniform2f(uR, canvas.width, canvas.height); gl.uniform1f(uT, ms / 1000);
  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
```
Add the same visibility and reduced-motion guards as other loops (render a single frame for reduced motion).

## Easing cheat sheet

| Feel | CSS cubic-bezier | GSAP |
|---|---|---|
| Smooth entrance | `.22, 1, .36, 1` | `power3.out` / `expo.out` |
| Balanced in-out | `.65, 0, .35, 1` | `power2.inOut` |
| Snappy exit | `.5, 0, .75, 0` | `power2.in` |
| Playful overshoot | `.34, 1.56, .64, 1` | `back.out(1.7)` |
| Springy | use `linear()` or JS spring | `elastic.out(1, .4)` |
