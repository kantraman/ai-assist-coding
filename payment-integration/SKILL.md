---
name: payment-integration
description: Research, plan, and implement a payment gateway or payment system integration (Stripe, Razorpay, PayPal, Adyen, Square, Braintree, Paytm, PhonePe, Cashfree, PayU, Mollie, Checkout.com, UPI, etc.) in a chosen programming language or framework. Use this skill whenever the user names a payment provider and/or asks to "integrate payments", "add checkout", "accept payments", "set up webhooks", "add subscriptions/refunds/payouts", "connect a payment gateway", or gives a payment system name plus a language (e.g. "Razorpay in Node.js", "Stripe with Python/Django"), even if they don't say "integration plan". The skill fetches the provider's current official docs, produces an implementation plan, then writes the code, webhook handling, tests and setup notes.
---

# Payment System Integration

Input the user gives: a **payment system** (e.g. Razorpay) and a **language/framework** (e.g. Node.js/Express). Output: a researched plan, then working, secure integration code.

Payment APIs change often (versions, deprecated endpoints, new required fields), and mistakes cost real money. So never write integration code from memory alone. Ground everything in the provider's current documentation, and design around the failure modes that matter in payments: forged callbacks, duplicate charges, lost webhooks, and leaked keys.

## Workflow

### 1. Clarify only what blocks progress
Infer defaults from the request and state them in one line. Ask (once, briefly) only if missing and material:
- Provider and language/framework (required; if the framework is unclear, pick the most common one for that language and say so)
- Payment flow: one-time payments, subscriptions, marketplace/split, payouts, or refunds (default: one-time checkout + refunds)
- Project state: new project, or an existing codebase to extend (if uploaded/present, read it first and match its conventions)

### 2. Research the provider's official docs
Use `web_search` then `web_fetch` on **official** sources only (provider docs, official SDK repos, changelog). Skip blog posts and forums unless docs are silent.

Collect and note the source URL for each:
- Current API/SDK version and the official SDK for the chosen language (or plain REST if none exists)
- Recommended integration path (e.g. hosted checkout vs. embedded/elements vs. server-to-server). Prefer the option that keeps card data off the user's servers, which minimizes PCI scope
- Authentication model (API keys, key id/secret, OAuth) and test vs. live mode
- Payment lifecycle: create order/intent → customer pays → confirm/capture → statuses
- **Signature/webhook verification** method, event names, retry behavior
- Idempotency support, refund API, rate limits, supported currencies/payment methods
- Test credentials, test card/UPI numbers, and a way to trigger test webhooks

If the docs can't be fetched (or search returns nothing usable), say so plainly, state what you are relying on from memory, mark those parts as **unverified**, and tell the user which doc pages to check.

If the user provides their own docs/files (PDF, OpenAPI spec), treat those as the primary source and read them with the appropriate file-reading approach.

### 3. Write the implementation plan
Present the plan in chat before coding (use `references/plan-template.md` for structure). Keep it concise: architecture/flow, endpoints to build, data model, env vars, security measures, test plan, go-live checklist, and assumptions or unverified items. For large integrations, pause for the user's go-ahead. For simple, clearly specified requests ("Stripe checkout in Flask"), state the plan briefly and continue straight into implementation.

### 4. Implement
Read `references/security-checklist.md` before writing code; every item there applies to every provider.

Build, in this order:
1. **Config**: environment variables via `.env.example` (never real secrets), loaded through the framework's standard mechanism
2. **Server-side payment creation**: amount and currency are determined on the server from your own catalog/order record, never trusted from the client
3. **Client/checkout step**: minimal frontend or redirect flow using the provider's hosted/embedded component
4. **Verification**: verify payment signature server-side after the client returns, *and* treat the webhook as the source of truth
5. **Webhook endpoint**: raw-body signature verification, idempotent event handling (dedupe by event id), fast 2xx response, safe handling of out-of-order events
6. **Order/payment persistence**: store provider ids, status, amount, currency; state transitions only move forward
7. **Refunds** (and subscriptions/payouts if in scope)
8. **Tests**: unit tests for signature verification and idempotency; instructions for end-to-end test-mode runs
9. **README**: setup, env vars, how to run, how to test webhooks locally (provider CLI or a tunnel), go-live steps

Code guidelines:
- Use the provider's official SDK when one exists for the language; otherwise a small typed REST client
- Match the idioms of the language/framework (async in Node/Python where natural, dependency injection in Spring, etc.)
- Amounts: use the provider's smallest currency unit as integers (paise/cents), never floats
- Log provider ids and statuses, never card data, full keys, or webhook secrets
- Pin dependency versions to what the docs currently recommend

### 5. Verify and hand off
- If the sandbox has network disabled, packages may not install; still run what you can (syntax check, linting, unit tests of pure logic) and say what was not run
- Deliver code as files (multiple files → a folder; present with `present_files`), with the README
- Summarize in a few lines: what was built, what to configure (keys, webhook URL, events to subscribe), what was verified vs. not, and any unverified doc assumptions
- Remind the user to test in the provider's test mode first and to complete the provider's account/KYC activation before going live

## Provider notes
Different regions favour different providers; if the user hasn't chosen one but describes a market (e.g. India: UPI, cards, netbanking), suggest 2 or 3 fitting options with one-line trade-offs and let them pick. Do not invent provider features. If a provider lacks something the user wants (e.g. no official SDK for their language), say so and propose the closest alternative.

## Things not to do
- Don't collect or store raw card numbers/CVV on the user's server
- Don't put secret keys in frontend code, repos, or logs
- Don't mark an order paid based only on a client-side redirect or callback
- Don't claim the integration is production-ready without a tested webhook path and the go-live checklist
- Don't present real-money actions (live charges, live payouts) as something to run during development
