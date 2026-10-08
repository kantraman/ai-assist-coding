# Payment Integration Security & Reliability Checklist

Apply to every provider. Each item exists because the failure it prevents has real financial consequences.

## Trust boundaries
- [ ] **Amount and currency are set server-side** from your own order/price data. A client-supplied amount lets buyers pay ₹1 for anything.
- [ ] **Never trust the browser redirect** ("payment success" page) as proof of payment. Verify the signature or retrieve the payment from the provider API server-side, and confirm final state via webhook.
- [ ] Verify the payment belongs to the order (match provider order/intent id, amount, and currency against your record).

## Webhooks
- [ ] Verify the signature using the **raw request body** (not re-serialized JSON) and the provider's documented algorithm (usually HMAC-SHA256). Framework JSON parsers often break this: capture the raw body for the webhook route.
- [ ] Use constant-time comparison for signatures.
- [ ] Check timestamp tolerance if the provider supports it (replay protection).
- [ ] **Idempotent processing**: store event ids with a unique constraint; ignore duplicates. Providers retry.
- [ ] Return 2xx quickly; do heavy work asynchronously (queue/background job).
- [ ] Handle out-of-order events; only allow forward state transitions (created → authorized → captured → refunded).
- [ ] Return non-2xx on signature failure; never process unsigned events.

## Secrets and data
- [ ] Keys live in environment variables / secret manager; `.env` is in `.gitignore`; `.env.example` has placeholders only.
- [ ] Secret keys never appear in frontend bundles, logs, or error messages. Only publishable/public keys go to the client.
- [ ] Do not store card numbers, CVV, or full track data. Use hosted fields/checkout so card data never touches your server (keeps PCI scope minimal, typically SAQ A).
- [ ] Separate test and live credentials; make the active mode obvious in config and logs.
- [ ] Mask or omit personal data in logs (email, phone, card last4 is fine).

## Reliability
- [ ] Use **idempotency keys** on create/charge/refund calls where the provider supports them, so network retries don't double-charge.
- [ ] Set timeouts and bounded retries with backoff on provider API calls.
- [ ] Reconciliation path: a job or admin action that re-fetches payment status from the provider for orders stuck in "pending".
- [ ] Refunds: guard against refunding more than the captured amount; record each refund with its provider id.
- [ ] Store amounts as integers in minor units (paise, cents); watch zero-decimal and three-decimal currencies (JPY, KWD).

## Web hygiene
- [ ] HTTPS only for checkout pages and webhook URLs.
- [ ] CSRF protection on your own payment endpoints (webhook route is exempt but signature-verified).
- [ ] Authenticate/authorize the user on create-order and refund endpoints; refunds should be admin-only.
- [ ] Rate-limit create-order and verify endpoints.

## Before going live
- [ ] Complete provider account activation/KYC.
- [ ] Swap to live keys via environment, register the live webhook URL and required events.
- [ ] Run one small real transaction and refund it.
- [ ] Alerting on webhook failures and on payments stuck in pending.
