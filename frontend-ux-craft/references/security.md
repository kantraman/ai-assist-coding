# Frontend security

**Mental model:** the browser is the person's machine, and everything shipped to it (JS, env vars,
props, source maps, API responses) is readable and modifiable by them. Frontend security therefore
has two jobs: (1) don't let *attackers* run code or steal data in a victim's browser (XSS, CSRF,
clickjacking, supply chain), and (2) never treat client-side checks as security; they're UX. Real
authorization, validation, and rate limiting live on the server.

## Contents
1. Ground rules
2. XSS: the sinks that matter, per framework
3. Sanitizing and Trusted Types
4. Content Security Policy and headers
5. Auth, sessions, tokens
6. CSRF and cross-origin
7. Secrets and configuration
8. Third-party code and dependencies
9. URLs, redirects, `postMessage`, iframes, windows
10. Sensitive data and privacy in the UI
11. Uploads and file handling
12. Auth UX that's secure *and* humane
13. Pre-ship security checklist

---

## 1. Ground rules

- **Client checks are cosmetic.** Hiding an "Admin" menu item is UX. The endpoint must enforce authorization. When showing/hiding UI by permission, the server sends a small set of capability booleans (`can.edit`), and every mutation is re-authorized server-side.
- **Validate on the client for people; validate on the server for safety.** Mirror rules so errors are friendly, but assume the client can be bypassed.
- **Anything in the bundle is public:** API keys, "hidden" routes, feature flags, comments, source maps, `VITE_*` / `NEXT_PUBLIC_*` / `NG_APP_*` / `PUBLIC_*` env vars, Inertia page props, SSR-serialized state. Only put in these what you'd be fine publishing.
- **Default to the framework's escaping** and treat every bypass API as a code-review red flag needing a written reason.
- Least privilege, least data: send the UI only the fields it renders.
- Fail closed: if a permission or flag can't be determined, hide/disable and let the server decide.

## 2. XSS: the sinks that matter, per framework

Modern frameworks escape text interpolation by default. XSS comes from **escape hatches** and DOM APIs:

| Ecosystem | Safe by default | Red-flag sinks (require sanitization + justification) |
|---|---|---|
| React | `{value}` in JSX | `dangerouslySetInnerHTML`, `href={userUrl}` / `src` with unvalidated schemes (`javascript:`), `ref.current.innerHTML`, `eval`/`new Function`, `<a {...userProps}>` spreading untrusted objects, server-rendering unescaped JSON into `<script>` |
| Vue | `{{ value }}`, `:attr` bindings | `v-html`, `:href`/`:src` with user URLs, `innerHTML` via refs, render functions with `innerHTML`, dynamic component/`is` from user input, templates compiled from user strings |
| Angular | `{{ value }}`, property bindings (auto-sanitized) | `bypassSecurityTrustHtml/Url/ResourceUrl/Script/Style`, `[innerHTML]` with content you've *bypassed*, `ElementRef.nativeElement.innerHTML`, `DomSanitizer` misuse, dynamic template compilation |
| Svelte | `{value}` | `{@html ...}`, `href` with untrusted schemes |
| Inertia (any adapter) | Adapter's escaping | Same as the adapter; plus **Blade**: `{!! !!}` and `@json` into inline scripts, unescaped `$page`/props rendered server-side |
| Any | | `document.write`, `insertAdjacentHTML`, `outerHTML`, `location = userInput`, `setTimeout("string")`, `postMessage` handlers that trust data, jQuery `.html()`, markdown renderers with raw HTML enabled |

**Rules**
1. Prefer rendering data as **text** or structured components. Need rich text from users (comments, CMS)? Render **Markdown → sanitized HTML** or a structured editor format (ProseMirror/TipTap JSON) → components.
2. Any URL derived from data must be **scheme-checked** (`https:`, `http:`, `mailto:`, `tel:` allowlist) before going into `href`/`src`/`action`/`formaction`. Relative URLs are safe; `javascript:` and `data:` are not.
3. Never build HTML strings by concatenation. Never `eval`. Never use `new Function`. Avoid inline event-handler attributes.
4. Serialize server state into HTML safely (the framework helper, or escape `<` as `\u003c`). A stray `</script>` in a string is an injection.
5. Watch **stored** content (profile names, filenames, chat) and **reflected** content (query params, error messages), not just "user input forms." Also DOM-based sources: `location.hash`, `document.referrer`, `window.name`, `postMessage`, `localStorage`.
6. Component libraries: when a prop accepts `string | ReactNode`, or `html`/`raw`, find out whether it inserts HTML.

## 3. Sanitizing and Trusted Types

- Sanitize with **DOMPurify** (or the platform `Sanitizer` API where supported), at the *point of insertion*, with a strict allowlist config (no `style`, no `iframe`, no `form` unless needed; forbid `data-*` if unused). Keep it up to date; sanitizer bypasses get patched.
- Sanitize **once, as late as possible, and right where you assign to the sink.** Don't sanitize at storage and assume it's safe forever, since the sink context may change.
- Enable **Trusted Types** via CSP (`require-trusted-types-for 'script'`) to make dangerous sinks throw unless given a vetted `TrustedHTML`. Create a single policy that wraps DOMPurify. It turns XSS-by-mistake into a build/test failure.
- Markdown: disable raw HTML in the renderer, or sanitize its output; validate link schemes; add `rel="noopener noreferrer nofollow ugc"` to user-supplied links.

## 4. Content Security Policy and headers

CSP is the safety net when a sink slips through. Set it on the server/CDN (meta CSP is weaker: no `frame-ancestors`, report-uri, etc.).

**A strong starting policy (nonce-based, for apps with SSR or an edge that can inject nonces):**
```
Content-Security-Policy:
  default-src 'self';
  script-src 'nonce-{RANDOM}' 'strict-dynamic';
  style-src 'self' 'nonce-{RANDOM}';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
  base-uri 'none';
  object-src 'none';
  form-action 'self';
  upgrade-insecure-requests;
  report-to csp-endpoint
```
- Roll out with `Content-Security-Policy-Report-Only` first; fix violations; then enforce.
- Avoid `'unsafe-inline'` and `'unsafe-eval'` for scripts. Static SPAs without a server per request can use **hashes** for inline scripts. Frameworks: Angular supports `ngCspNonce`; Next.js middleware nonces; Laravel (via a CSP package) and Vite manifests can emit nonces; Vue/React SPAs should avoid inline script and use external bundles.
- Inline styles from libraries (some UI kits, `style=""` attributes) may force `style-src 'unsafe-inline'`; prefer nonce/hashes or CSS variables + classes, and accept a slightly looser `style-src` over a looser `script-src`.

**Other response headers (server/CDN):**
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin` (or stricter)
- `Permissions-Policy:` disable camera/mic/geolocation etc. unless used
- `Strict-Transport-Security` (HSTS) with `includeSubDomains` once HTTPS is solid
- `Cross-Origin-Opener-Policy: same-origin` (and `Cross-Origin-Embedder-Policy` if you need cross-origin isolation)
- Clickjacking: `frame-ancestors 'none'` (or specific origins); `X-Frame-Options: DENY` as legacy backup
- `Cache-Control: no-store` on responses with sensitive data / authenticated pages

If you're writing frontend code only, **include the recommended headers in the deliverable notes** (or as server/CDN config) rather than silently skipping them.

## 5. Auth, sessions, tokens

- **Prefer server-managed sessions in `HttpOnly; Secure; SameSite=Lax|Strict` cookies** (Laravel session/Sanctum SPA mode, framework session, or a Backend-for-Frontend that holds tokens). JavaScript can't read `HttpOnly` cookies, so XSS can't exfiltrate them.
- **Avoid storing access/refresh tokens in `localStorage`/`sessionStorage`**: any XSS reads them. If a token must live in JS (pure SPA + third-party API), keep it in memory, short-lived, with refresh via `HttpOnly` cookie, and accept the tradeoff explicitly.
- OAuth/OIDC in browsers: **Authorization Code + PKCE**, never implicit flow; validate `state`; exact redirect URIs; don't put tokens in URLs.
- Logout: server-side invalidation + clear client state (query caches, stores, IndexedDB, service worker caches). Shared computers matter. Sensitive pages shouldn't be restorable via bfcache after logout (`Cache-Control: no-store`).
- Session expiry: detect 401/419 globally; preserve unsaved work; redirect to sign-in with a validated return URL; be gentle: "Your session ended. Sign in to continue. Your draft is saved."
- MFA/step-up UX: clear, accessible, supports paste/autofill (`autocomplete="one-time-code"`), passkeys where available.

## 6. CSRF and cross-origin

- Cookie-authenticated state-changing requests need CSRF defense: `SameSite` cookies plus an anti-CSRF token or custom header. Frameworks help: Laravel's `XSRF-TOKEN` cookie → `X-XSRF-TOKEN` header (Axios does this automatically; with raw `fetch` you must set the header yourself); Angular `HttpClient` XSRF support (`withXsrfConfiguration`); Django/Rails equivalents.
- **Never** perform state changes on `GET`.
- **CORS is not a security control for your UI**; it restricts what *other origins' scripts* can read. Configure narrowly: exact origins, no `*` with credentials, minimal methods/headers.
- Send `credentials: 'include'` only to your own API origins.
- Rate-limit and lockout are server jobs, but the UI should handle 429 gracefully (retry-after message, no hammering).

## 7. Secrets and configuration

- Anything with a public prefix (`VITE_`, `NEXT_PUBLIC_`, `NG_APP_`, `PUBLIC_`, Laravel `MIX_/VITE_`) ships to the browser. **Never** put private API keys, DB URLs, signing secrets, or admin tokens there. Publishable keys (Stripe publishable, Maps with referrer restrictions) are fine but must be **restricted** at the provider.
- Move secret-bearing calls behind your server/BFF or a serverless function.
- Don't commit `.env`; add secret scanning (gitleaks/trufflehog) to CI; rotate anything that leaked.
- Disable or restrict **production source maps** (or upload them privately to your error tracker) unless you're deliberately public.
- Strip debug logging; don't print tokens, PII, or full API payloads to the console.

## 8. Third-party code and dependencies

- Every `<script>` from another origin has full power over your page. Minimize; self-host critical libs; use **Subresource Integrity** (`integrity="sha384-…" crossorigin="anonymous"`) for CDN assets that must stay external.
- Tag managers and analytics are the biggest hidden attack surface: restrict who can publish tags; consider sandboxed iframes; review data they receive.
- Dependencies: commit lockfiles; `npm ci` in CI; enable Dependabot/Renovate; `npm audit` / OSV scanner; prefer few, well-maintained packages; be wary of typosquats and new maintainers; consider `--ignore-scripts` for installs and provenance checks; pin GitHub Actions by SHA.
- Before adding a package: does the platform already do this? Is it maintained? What does it pull in? A left-pad-sized package is a liability.
- Review UI kits that render user-provided HTML or run `eval`.

## 9. URLs, redirects, `postMessage`, iframes, windows

- **Open redirects:** `?next=`, `returnTo`, `redirect_uri` must be validated: allow only same-origin relative paths (starts with a single `/`, not `//` or `/\`) or an explicit allowlist; parse with `new URL(x, location.origin)` and compare `origin`.
- Links with `target="_blank"` → add `rel="noopener noreferrer"` (modern browsers imply `noopener`, but be explicit and keep `noreferrer` when leaking the URL matters).
- **`postMessage`:** always specify the exact `targetOrigin` when sending (never `"*"` with sensitive data); when receiving, **check `event.origin`** against an allowlist and validate the message shape.
- **Iframes:** use `sandbox` with the minimum flags (never `allow-scripts` + `allow-same-origin` together on untrusted content), `allow` for permissions, `referrerpolicy`, and `loading="lazy"`. Embedding third-party widgets = trusting them.
- Don't put secrets, tokens, or PII in URLs/query strings (they land in logs, history, referrers, analytics).
- `window.open` / `location.assign` with user-controlled values = same scheme/origin validation as links.

## 10. Sensitive data and privacy in the UI

- Show only what's needed; **mask** by default (`•••• 4242`, reveal on demand with logging server-side); never prefill full card numbers or SSNs.
- `autocomplete` correctly: `off` is not guaranteed for passwords; use `new-password`/`current-password`; for truly sensitive one-time fields use appropriate tokens or `autocomplete="off"` + `inputmode`; don't break password managers.
- Keep PII out of: analytics events, error-tracker payloads, `console`, URLs, `localStorage`, client caches that survive logout. Scrub before sending (Sentry `beforeSend`, etc.).
- Screen sharing / shoulder surfing: blur or mask sensitive fields on inactivity if the domain warrants (finance/health).
- Clipboard/permissions: request permissions **in context** after a user gesture, explain why, handle denial gracefully.
- Cookie/consent UX: honest defaults, symmetric accept/reject, no dark patterns. Accessible dialogs.
- Error messages don't disclose internals ("User not found" vs. "Email or password is incorrect" on login; no stack traces or SQL).
- Caching: authenticated API responses shouldn't be cached in shared caches; service workers must not cache private data across users.

## 11. Uploads and file handling

- Client-side type/size checks are **UX only**; the server validates content type, size, and scans. Show clear limits up front.
- Preview using `URL.createObjectURL` and revoke it after; don't inject file contents as HTML. Treat **SVG** as active content (scripts inside): render via `<img>` or sanitize, don't inline user SVG.
- Serve user uploads from a **separate origin/domain** with `Content-Disposition` and `nosniff`.
- Filenames from users are untrusted: escape when rendering, don't build paths from them.
- Accessible upload: real `<input type="file">` (visually styled label), drag-and-drop is an enhancement, progress announced, errors per-file.

## 12. Auth UX that's secure *and* humane

- Login errors: generic ("The email or password is incorrect") to avoid account enumeration; the *forgot-password* flow says "If an account exists, we've sent a link."
- Never block paste. Show/hide password toggle. Don't force arbitrary complexity rules; prefer length + breached-password checks + strength meter (advisory) and passkeys/magic links.
- Rate-limit feedback: "Too many attempts. Try again in 10 minutes." with a real time.
- Confirm sensitive actions (email change, delete account, payment method) with re-auth, and notify by email.
- Destructive/irreversible + privileged operations get **explicit, named** confirmation, and audit trail on the server.
- Session/device management page so people can see and revoke access, a security *feature* that builds trust.

## 13. Pre-ship security checklist

- [ ] No `dangerouslySetInnerHTML` / `v-html` / `{@html}` / `bypassSecurityTrust*` / `innerHTML` on untrusted data; any exception is sanitized + commented
- [ ] All user-supplied URLs scheme-validated; `next`/`redirect` params allowlisted
- [ ] CSP (report-only → enforce), `frame-ancestors`, `nosniff`, `Referrer-Policy`, HSTS recommended to the person
- [ ] Auth via HttpOnly cookies/BFF; no tokens in `localStorage`; logout clears client state
- [ ] CSRF handled for cookie auth; no state change on GET
- [ ] No secrets in bundle/env-public vars/source maps/repo; publishable keys restricted
- [ ] Third-party scripts minimized, SRI where external; lockfile + audit in CI
- [ ] `postMessage` origin-checked; iframes sandboxed; `target=_blank` has `rel`
- [ ] PII kept out of URLs, logs, analytics, error payloads, persisted client storage
- [ ] Authorization enforced server-side; UI capability flags are cosmetic
- [ ] Uploads validated server-side; user SVG/HTML never inlined raw
- [ ] Errors are helpful but non-revealing; 401/403/429 handled gracefully
