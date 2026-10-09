# Engineering documentation (FE, BE, QA, DevOps)

Goal: a frontend engineer can integrate, a backend engineer can maintain, and an ops engineer can deploy and debug - each without a meeting.

## Contents
1. API reference (conventions + per-endpoint template)
2. Error catalogue
3. Data models
4. FE-BE contract (what the UI must honour)
5. Setup and operations runbook
6. Changelog and breaking-change policy
7. Worked endpoint example

---

## 1. API reference

### 1a. Conventions section (write once, at the top)
Document everything that applies to all endpoints so it is not repeated:

| Topic | What to state |
|---|---|
| Base URLs | One per environment (dev, staging, prod), with version prefix |
| Authentication | Scheme (Bearer JWT, API key, cookie session), how to obtain a token, lifetime, refresh flow, header format |
| Authorisation | Roles/permissions model and where it is enforced |
| Content types | Request and response media types, charset |
| Versioning | How versions are expressed, deprecation policy |
| Pagination | Style (offset/cursor), parameter names, defaults, max page size, response envelope |
| Filtering and sorting | Syntax, allowed fields |
| Dates, times, money, IDs | ISO 8601 + timezone rule, currency representation (minor units?), ID format |
| Idempotency | Which endpoints are safe to retry, idempotency-key header if any |
| Rate limits | Limits, headers returned, behaviour on exceed (429 + Retry-After) |
| Response envelope | Shape of success and error bodies |
| Null vs absent | Whether optional fields are omitted or null |

### 1b. Per-endpoint template
Use this exact set of fields for every endpoint, so readers know where to look.

```markdown
### <METHOD> <path>  - <Short action title>
Status: stable | in progress | planned | deprecated
Auth: required (roles: ...) | public
Purpose: one or two sentences, including business context where non-obvious.

**Path parameters** (table: name, type, description)
**Query parameters** (table: name, type, required, default, constraints, description)
**Headers** (only those beyond the global ones)
**Request body** (table: field, type, required, constraints, description) + JSON example
**Success response** - status code, body table, JSON example
**Error responses** - table of status, error code, when it happens, how the client should react
**Side effects** - emails sent, events published, records created elsewhere, cache invalidation
**Idempotency / concurrency** - safe to retry? optimistic locking?
**Notes** - edge cases, ordering guarantees, performance characteristics
```

Rules:
- Constraints are numbers and formats, not adjectives: `string, 3-50 chars, ^[a-z0-9_]+$`.
- Every field table says whether the field is **required**, **nullable**, and **read-only**.
- Every endpoint shows at least one success and one error example that are valid against the schema.
- Document enum values exhaustively, with meaning for each.
- State what the server does with unknown fields (ignored or rejected).

## 2. Error catalogue
One table for the whole API:

| HTTP | Code | Meaning | Typical cause | Client action |
|---|---|---|---|---|

Include validation error shape (how field-level errors are returned), auth errors (401 vs 403 distinction), conflict and rate-limit errors, and 5xx behaviour (retry or not). Add the correlation/request-ID header if one exists so support can trace issues.

## 3. Data models
For each core entity: fields with types and constraints, relationships, lifecycle/state machine (use a Mermaid `stateDiagram-v2` when there are more than two states), soft vs hard delete, and which fields are computed or immutable. Add an ER diagram (Mermaid `erDiagram`) for the main relationships.

## 4. FE-BE contract
The API reference tells FE what the server accepts. This section tells FE what the *experience* must handle. Include:

- **Validation rules mirrored in the UI**: list rules the server enforces so the UI can validate early; state that the server is still the authority.
- **UI states per screen/flow**: loading, empty, error, partial, success, and what data drives each.
- **Permissions matrix**: role x action -> allowed/denied, and how the UI should present denied actions (hidden vs disabled).
- **Feature flags and config** the UI reads, with default values.
- **Real-time or async behaviour**: polling intervals, websocket events, eventual consistency windows, long-running job status flow.
- **Caching and staleness**: what FE may cache and for how long, ETag/If-None-Match use.
- **Sequencing dependencies**: calls that must happen in order (e.g. create upload session -> upload -> confirm).
- **Agreed deviations**: anywhere FE and BE agreed on behaviour that is not obvious from the schema.
- **Open contract questions** with owner and due date.

## 5. Setup and operations runbook
- **Prerequisites**: runtime versions, tools, accounts.
- **Local setup**: clone, install, configure, seed data, run, verify (include a "you should see..." check).
- **Configuration**: table of every environment variable - name, purpose, required, example/placeholder, default, which environments differ. Never include real secrets.
- **Build and deploy**: pipeline stages, how to promote between environments, rollback procedure.
- **Dependencies**: databases, queues, third-party APIs, with failure impact ("if X is down, Y degrades like...").
- **Monitoring and logging**: where logs live, key metrics, alerts, dashboards, how to trace a request.
- **Troubleshooting**: symptom -> likely cause -> check -> fix, for the top failure modes you can verify from the code or from the user.
- **Backups, migrations, data retention**: procedures and schedules if applicable.
- **Security notes**: secret management, auth boundaries, known sensitive endpoints.
- **Testing**: how to run unit/integration/e2e tests, test accounts, seed fixtures.

## 6. Changelog and breaking changes
Keep a dated changelog (Added / Changed / Deprecated / Removed / Fixed). For every breaking change add: what changed, who is affected, migration steps, effective date. Put breaking changes at the top of the release entry.

## 7. Worked example (endpoint)

```markdown
### POST /v1/orders - Create an order
Status: stable
Auth: required (roles: customer, admin)
Purpose: Creates an order from the caller's current cart and reserves stock. Payment is collected separately via `POST /v1/orders/{id}/pay`.

**Request body**
| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| cartId | string (uuid) | yes | must belong to caller | Cart to convert |
| shippingAddressId | string (uuid) | yes | must belong to caller | Delivery address |
| notes | string | no | max 500 chars | Delivery notes |

```json
{ "cartId": "6f1c0b0e-1c2a-4a43-9a3a-5d3b2d4f9a10", "shippingAddressId": "b7d1...", "notes": "Leave at the door" }
```

**Success - 201 Created**
```json
{ "id": "ord_1042", "status": "pending_payment", "total": { "amount": 4599, "currency": "USD" }, "createdAt": "2026-01-15T10:22:31Z" }
```
`total.amount` is in minor units (cents).

**Errors**
| Status | Code | When | Client action |
|---|---|---|---|
| 400 | VALIDATION_FAILED | Missing/invalid field; details in `errors[]` | Show field errors |
| 404 | CART_NOT_FOUND | cartId unknown or not owned by caller | Refresh cart |
| 409 | INSUFFICIENT_STOCK | An item sold out since being added | Show affected items from `details.items` |
| 429 | RATE_LIMITED | >30 requests/min | Retry after `Retry-After` seconds |

**Side effects**: stock reserved for 15 minutes; `order.created` event published.
**Idempotency**: send `Idempotency-Key` header; repeated key within 24h returns the original response.
```
