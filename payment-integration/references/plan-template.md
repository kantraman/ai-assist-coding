# Implementation Plan Template

Use this structure for the plan shown before coding. Keep each section short; drop sections that don't apply.

```
# <Provider> integration in <Language/Framework>

## Scope and assumptions
- Flow: <one-time / subscription / refunds / payouts>
- Project: <new / existing, conventions detected>
- Assumptions: <anything inferred, one line each>

## Sources consulted
- <doc title>: <URL> (API/SDK version noted)
- Unverified items: <list, or "none">

## Architecture / payment flow
1. Client requests checkout → server creates order/intent (amount from server-side data)
2. Client completes payment via <hosted page / embedded component>
3. Server verifies signature/status on return
4. Provider webhook confirms final status → order marked paid (source of truth)
(Include a small mermaid or ASCII sequence if the flow is non-trivial.)

## Components to build
| Piece | Purpose | Path |
|-------|---------|------|
| Config | env vars, client init | ... |
| Create-order endpoint | ... | POST /api/payments/create |
| Verify endpoint | ... | POST /api/payments/verify |
| Webhook handler | ... | POST /api/webhooks/<provider> |
| Refund endpoint | ... | POST /api/payments/:id/refund |
| Persistence | payments table/model | ... |
| Tests | signature, idempotency, state transitions | ... |

## Data model
payments: id, order_id, provider_payment_id, provider_order_id, amount_minor, currency, status, created_at, updated_at
webhook_events: event_id (unique), type, processed_at

## Environment variables
- <PROVIDER>_KEY_ID, <PROVIDER>_KEY_SECRET, <PROVIDER>_WEBHOOK_SECRET, ...

## Security measures
- Server-side amount, signature verification, idempotent webhooks, secrets in env, HTTPS only

## Test plan
- Unit: signature verification, duplicate webhook, out-of-order events
- Manual: test-mode success, failure, refund; local webhook via <CLI/tunnel>

## Go-live checklist
- Live keys, webhook URL + events registered, account/KYC activation, HTTPS, monitoring/alerts
```
