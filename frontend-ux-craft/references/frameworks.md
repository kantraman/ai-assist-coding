# Framework notes: React, Angular, Vue, Inertia, Svelte

The design system (tokens, placement contract, component contracts) is **framework-agnostic**: same
`DESIGN.md`, same `tokens.css`. This file is only about how to express it idiomatically in each stack
and the gotchas that trip people up. Read only the section(s) for the stack in use, plus §0.

## Contents
0. Applies to every stack
1. React (and Next.js / Remix / Vite SPA)
2. Angular
3. Vue (and Nuxt)
4. Inertia.js (Laravel + Vue / React / Svelte)
5. Svelte / SvelteKit
6. Choosing a component foundation

---

## 0. Applies to every stack

- **Existing project?** Follow `redesign-existing.md`; its §10 has stack-specific migration notes (view encapsulation, `::ng-deep`, Inertia layouts, Tailwind/CSS-in-JS token bridging).
- **Detect before deciding.** Read `package.json`, the existing components, styling approach, and lint config. Match conventions: file layout, naming, state management, CSS strategy. Never introduce a second UI library or styling system without saying why.
- **SPA navigation breaks default browser behavior.** Full page loads reset focus, announce the new title, and scroll to top. Client-side routing does none of that. On every route change: update `document.title`, move focus to the new `<h1>` (`tabindex="-1"`), reset scroll unless restoring, and (optionally) announce via live region. Skip it on first load.
- **Headless primitives + your tokens** is the strongest combo for both accessibility and distinctiveness: behavior/ARIA from a library; visuals entirely yours.
- One global **live region** in the app shell for status messages ("Saved", "Copied"); expose an `announce()` helper.
- Lint accessibility in CI (`jsx-a11y`, `angular-eslint` template rules, `vuejs-accessibility`), plus axe in component/E2E tests (`jest-axe`, `@axe-core/playwright`, `cypress-axe`).
- Prefer a real `<form>` with `onSubmit`/`@submit.prevent`/`(ngSubmit)` so Enter works and password managers behave.
- Keep server state (fetched data) separate from UI state; give every async view all its states (loading, empty, error, success).
- Type props/inputs. Types double as documentation of the component contract.

## 1. React

**Foundation:** Radix Primitives, React Aria (Components), Ark UI, or Headless UI for behavior. shadcn/ui is copy-in Radix + Tailwind: **restyle it via your tokens**; shipping it with default radii, shadows, and slate/zinc palette produces the generic look this skill exists to avoid.

**Patterns**
```tsx
// One Field used by every input: ids and aria wiring live here, once.
function Field({ label, hint, error, children }: FieldProps) {
  const id = useId();
  const hintId = hint ? `${id}-hint` : undefined;
  const errId = error ? `${id}-err` : undefined;
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {hint && <p id={hintId} className="hint">{hint}</p>}
      {cloneElement(children, {
        id, 'aria-invalid': !!error || undefined,
        'aria-describedby': [hintId, errId].filter(Boolean).join(' ') || undefined,
      })}
      {error && <p id={errId} className="error"><Icon name="alert" aria-hidden /> {error}</p>}
    </div>
  );
}
```
```tsx
// Route-change focus (React Router). Skip the first render.
function RouteAnnouncer() {
  const { pathname } = useLocation();
  const first = useRef(true);
  useEffect(() => {
    if (first.current) { first.current = false; return; }
    const h1 = document.querySelector<HTMLElement>('h1');
    h1?.setAttribute('tabindex', '-1'); h1?.focus();
  }, [pathname]);
  return null;
}
```
(Next.js App Router ships its own route announcer; still manage focus for in-page transitions and dialogs.)

**Gotchas**
- Don't `onClick` on `div`/`span`. Use `button`/`a`. Use `<Link>` (framework router) for navigation so URLs are real.
- React 19: `useActionState`, `useFormStatus`, `useOptimistic` give clean pending/optimistic UI for forms; still wire `aria-busy` and announcements yourself. `useTransition` keeps the UI responsive during navigations.
- Error boundaries per region + `Suspense` with skeleton fallbacks that match final layout.
- Effects for focus management need care: focus after the element is mounted (`useEffect`/`useLayoutEffect`, or `autoFocus` only where appropriate).
- Avoid index keys on reorderable lists (focus and state jump).
- Keep styles in tokens: Tailwind utilities that reference role variables, CSS Modules, or vanilla-extract. Avoid inline `style` for themable values.
- Security: no `dangerouslySetInnerHTML` without DOMPurify; validate URL schemes before `href`; don't spread untrusted objects into elements; in Next.js, server-only secrets never in `NEXT_PUBLIC_*`, and Server Actions are public endpoints (authorize inside each).

## 2. Angular

**Foundation:** Angular CDK (a11y: `FocusTrap`, `LiveAnnouncer`, `FocusMonitor`, `ListKeyManager`; overlay; a11y-friendly menus/dialog primitives) and/or Angular Material (M3). Themed via tokens: bridge your role variables to Material's system tokens so both worlds share a palette.

**Patterns (modern Angular: standalone components, signals, built-in control flow)**
```ts
// Field owns the ids; a directive on the projected control picks them up via DI.
@Component({
  selector: 'app-field',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <label [for]="id">{{ label() }}</label>
    @if (hint()) { <p [id]="id + '-hint'" class="hint">{{ hint() }}</p> }
    <ng-content />
    @if (error()) { <p [id]="id + '-err'" class="error" role="alert">{{ error() }}</p> }
  `,
})
export class FieldComponent {
  private static n = 0;
  readonly id = `fld-${FieldComponent.n++}`;
  label = input.required<string>();
  hint = input<string>();
  error = input<string>();
  describedBy = computed(() =>
    [this.hint() && `${this.id}-hint`, this.error() && `${this.id}-err`].filter(Boolean).join(' ') || null);
}

@Directive({
  selector: '[appFieldControl]',
  standalone: true,
  host: {
    '[id]': 'field.id',
    '[attr.aria-describedby]': 'field.describedBy()',
    '[attr.aria-invalid]': 'field.error() ? true : null',
  },
})
export class FieldControlDirective { field = inject(FieldComponent); }
// <app-field label="Email" [error]="err"><input appFieldControl type="email" autocomplete="email" formControlName="email"></app-field>
```
```ts
// Route-change focus + title. Register once (e.g. in app initializer).
inject(Router).events.pipe(filter(e => e instanceof NavigationEnd)).subscribe(() => {
  const h1 = document.querySelector<HTMLElement>('h1');
  h1?.setAttribute('tabindex', '-1'); h1?.focus();
});
// Titles: set `title` on routes or provide a custom TitleStrategy for "Page · Section · App".
```

**Gotchas**
- **Reactive Forms** with typed controls; custom controls implement `ControlValueAccessor` so they work with `formControlName`/`ngModel`. Show errors on `touched` or after submit; link with `aria-describedby`; focus the first invalid control on failed submit (loop the form's controls or use a directive).
- Use `@for` with `track`; use `OnPush` + signals to keep change detection cheap.
- Templates: `angular-eslint` template-accessibility rules on; `(click)` on non-interactive elements is flagged. Fix it.
- Structural focus: `cdkTrapFocus` + `cdkTrapFocusAutoCapture` for dialogs; return focus on close.
- Material customization: don't fight component internals with `::ng-deep`/`!important`; use theming/density APIs and tokens, or wrap components.
- Security: Angular sanitizes `[innerHTML]`, `[href]`, `[src]` automatically. **Never** call `DomSanitizer.bypassSecurityTrust*` on data you didn't author; avoid `ElementRef.nativeElement.innerHTML`; use `HttpClient`'s built-in XSRF support with cookie auth; support CSP nonces via `ngCspNonce` on the root element; prefer HttpOnly cookie sessions over tokens in storage; use route guards for UX but authorize on the server.
- SSR/hydration: avoid direct DOM access outside `afterNextRender`/platform checks.

## 3. Vue (3.x, Nuxt)

**Foundation:** Reka UI (successor to Radix Vue), Headless UI (Vue), or PrimeVue/Nuxt UI themed through tokens; Vuetify only if the project already uses it.

**Patterns (`<script setup>` + composables)**
```vue
<script setup lang="ts">
import { computed, useId } from 'vue'
const props = defineProps<{ label: string; hint?: string; error?: string }>()
const id = useId() // Vue 3.5+
const describedBy = computed(() =>
  [props.hint && `${id}-hint`, props.error && `${id}-err`].filter(Boolean).join(' ') || undefined)
</script>

<template>
  <div class="field">
    <label :for="id">{{ label }}</label>
    <p v-if="hint" :id="`${id}-hint`" class="hint">{{ hint }}</p>
    <slot :id="id" :described-by="describedBy" :invalid="!!error" />
    <p v-if="error" :id="`${id}-err`" class="error" role="alert">{{ error }}</p>
  </div>
</template>
```
```ts
// Route-change focus + title
router.afterEach(async (to, from) => {
  if (to.fullPath === from.fullPath) return
  await nextTick()
  const h1 = document.querySelector<HTMLElement>('h1')
  h1?.setAttribute('tabindex', '-1'); h1?.focus()
})
```

**Gotchas**
- `v-model` on custom components: define `defineModel()` (3.4+) and keep native attributes flowing via `v-bind="$attrs"` (and `inheritAttrs: false` when the root isn't the input).
- Use `<Teleport to="body">` for dialogs/popovers so stacking and focus trapping behave; ensure `inert` on the app root while open.
- `<Transition>`: honor `prefers-reduced-motion` in the CSS classes.
- Scoped styles + tokens: components use `var(--role)`; `v-bind()` in CSS only for truly dynamic values.
- Use `key` on lists and on route-view when you need state reset; keep `<KeepAlive>` from resurrecting stale sensitive data after logout.
- Security: avoid `v-html` (sanitize when unavoidable); validate `:href`/`:src` from data; don't compile templates from user strings; Nuxt `runtimeConfig.public.*` is public, so secrets go in private runtime config used server-side only.
- Nuxt: `useHead`/`useSeoMeta` for titles; `<NuxtRouteAnnouncer>` exists in recent versions but verify focus behavior yourself.

## 4. Inertia.js (Laravel + Vue / React / Svelte)

Inertia gives SPA feel with server routing. That changes a few things that matter for UX and security.

**Accessibility & UX**
- Navigations are XHR + component swap: **no focus reset, no title announcement**. Add a global handler:
```ts
import { router } from '@inertiajs/vue3' // or '@inertiajs/react' / '@inertiajs/svelte'
router.on('navigate', () => {
  const h1 = document.querySelector<HTMLElement>('h1')
  h1?.setAttribute('tabindex', '-1'); h1?.focus()
})
```
  Set titles with `<Head title="Invoice 1042 · Billing" />` per page (and a `title` callback in `createInertiaApp` for the suffix).
- **Persistent layouts** (`Page.layout = AppLayout`, or `layout` in `<script>`): nav, live region, and toast host survive navigations so state, focus rings in nav, and scroll positions behave.
- **Forms:** use `useForm`. Render `form.errors.field` under each field (linked by `aria-describedby`), keep input on failure (`preserveScroll`, `preserveState` where needed), reflect `form.processing` with `aria-busy` + "Saving…" label (don't unmount the button), and on `onError` focus the first invalid field or an error summary. Show `form.recentlySuccessful` as a transient inline "Saved" (via live region).
- **Flash messages** come through shared props: render them into the persistent live region/toast host, once per navigation (guard against re-showing on back/forward).
- **Loading states:** use the progress indicator config (`progress: { color: 'var(--brand)' }` and make it accessible or supplement with a live region), **Deferred props** (`<Deferred data="stats" fallback={…}>`; skeleton matching the final layout), `WhenVisible`, and **prefetching** on `<Link prefetch>` for snappy feel.
- Links: `<Link href>` for navigation (real anchors), `method="post"` links must be buttons (`as="button"`) semantically.
- Error pages: return proper 403/404/419/500 as Inertia pages with helpful copy and a way back, not the default modal or raw dev error page.
- Modals / slide-overs driven by routes (via community packages or nested layouts) still need focus trap, `Esc`, restore focus, and a URL.

**Security**
- **Everything in page props is visible to the client** (it's serialized in the HTML/JSON). Return only the fields the page renders: use API Resources/DTOs, never whole Eloquent models (`$hidden` isn't a safety net for everything). Audit `HandleInertiaRequests::share()`: `auth.user` should be a minimal set (id, name, avatar, permissions/`can` flags), not the model.
- Authorization stays in **Policies/Gates/middleware** on every controller action; `can.*` flags only shape the UI. Also authorize **prop-loading closures** and deferred props.
- **CSRF:** Inertia + Axios uses Laravel's `XSRF-TOKEN` cookie → `X-XSRF-TOKEN` header automatically. If you use raw `fetch` for extra requests, add the header. Handle **419** (expired) gracefully: prompt to refresh, keep the user's input.
- Validation lives on the server (`FormRequest`); the client renders returned errors. Don't trust client rules.
- Blade root view: never inject unescaped values (`{!! !!}`) into it; pass a **CSP nonce** into the root `<script>`/`@vite` tags if you enforce nonce-based CSP.
- SSR (Inertia SSR): treat the Node SSR server as an internal service; escape serialized state; don't leak server-only data into props "because SSR needs it."
- Version mismatch (409) and session-expiry redirects: make sure they land the person somewhere sensible with their work preserved.

## 5. Svelte / SvelteKit

- Use `bind:`/actions for focus management (`use:focusOnMount`); `svelte:head` for titles; keyboard handlers on interactive elements only (the compiler's a11y warnings are good. Don't silence them).
- `{@html}` is the XSS sink; sanitize. `$env/static/public` and `PUBLIC_*` are public; private env stays server-side.
- SvelteKit form actions + `use:enhance` give progressive enhancement: keep forms working without JS, then improve. Re-focus and announce after `enhance` updates.
- Transitions: respect reduced motion (`prefers-reduced-motion` check in custom transitions).

## 6. Choosing a component foundation

| Situation | Suggest |
|---|---|
| Distinctive brand, custom look, accessibility must be right | Headless primitives (Radix / React Aria / Reka UI / Headless UI / Angular CDK) + own styles on tokens |
| Enterprise internal tool, speed over identity, Angular | Angular Material (M3) themed via tokens |
| Existing library in the codebase | Keep it; theme via its token API; wrap for gaps |
| Prototype in an hour | Whatever the stack's popular kit is, but still move colors/type/radius to tokens so the prototype doesn't harden into a template |
| Design-system for multiple frameworks | Tokens in CSS variables (or Style Dictionary) + Web Components/Lit for the shared atoms, or per-framework thin wrappers |

Whatever the choice: override the library's *default look* on purpose (type, radius by role, elevation, spacing density, focus ring, motion). Untouched defaults are what make different products look identical.
