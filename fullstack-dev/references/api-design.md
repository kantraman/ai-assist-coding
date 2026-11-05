# API Design

## Contents
1. Contract first
2. Resources and endpoints
3. Requests, responses, errors
4. Pagination, filtering, sorting
5. Safety: idempotency, concurrency, rate limits
6. AuthN and AuthZ
7. Choosing REST, GraphQL, gRPC, tRPC
8. Performance
9. Testing the contract
10. API security checklist

## 1. Contract first

Write the OpenAPI (or GraphQL SDL / protobuf) before handlers. Generate or validate types from it so server, client, and docs cannot drift. Each endpoint node in the graph links to a requirement and a test.

## 2. Resources and endpoints

- Nouns, plural, hierarchical only when ownership is real: `/orders/{id}/items`. Avoid deep nesting beyond two levels.
- Methods: GET safe and cacheable, POST create/actions, PUT replace, PATCH partial update, DELETE remove. Model non-CRUD actions as sub-resources (`POST /orders/{id}/cancellations`).
- Status codes: 200, 201 (+ `Location`), 202 for async jobs, 204, 400 validation, 401 unauthenticated, 403 forbidden, 404, 409 conflict, 422 semantic, 429 rate limited, 5xx server faults.
- Version in the path or header (`/v1`). Changes are additive within a version; breaking changes need a new version and a deprecation window.

## 3. Requests, responses, errors

- Validate every input at the boundary with a schema (Zod, Pydantic, Bean Validation, FluentValidation, etc.): types, ranges, lengths, enums, unknown fields rejected or ignored by policy.
- Never expose ORM entities directly; map to response DTOs so internal columns do not leak (mass assignment protection: explicit allow-lists for writable fields).
- Errors use one shape (RFC 9457 `application/problem+json`): `type`, `title`, `status`, `detail`, `instance`, plus `errors[]` for field issues and a `correlation_id`. Never include stack traces or SQL.
- Consistent naming and formats: ISO 8601 UTC timestamps, string ids, money as integer minor units + currency.

## 4. Pagination, filtering, sorting

- Cursor pagination for lists: `?limit=50&cursor=...`; response includes `next_cursor`. Cap `limit` server-side.
- Filters as explicit, validated query params; sort fields from an allow-list that matches existing indexes.
- Sparse fields or expansion (`?expand=items`) only when it prevents real over/under-fetching.

## 5. Safety

- **Idempotency**: unsafe retried calls (payments, order creation) accept `Idempotency-Key`; store key + response for a window.
- **Optimistic concurrency**: `ETag` / `If-Match` or a `version` field; return 409/412 on conflict.
- **Rate limiting**: per identity and per IP with `429` + `Retry-After`; stricter on auth endpoints.
- **Async work**: return `202` with a status resource; do not hold requests for long jobs.
- **Webhooks**: sign payloads (HMAC), include timestamp, retry with backoff, make consumers idempotent.

## 6. AuthN and AuthZ

- Browser apps: server-side sessions or short-lived tokens in `HttpOnly; Secure; SameSite` cookies, with CSRF protection for cookie auth. Public/mobile/third-party clients: OAuth 2.1 / OIDC with PKCE. Do not store long-lived tokens in `localStorage`.
- Passwords: Argon2id or bcrypt via the framework's vetted library; never custom crypto. Offer MFA for sensitive apps.
- **Authorize on the server for every object access** (not only per route): check the caller may act on *this* resource (prevents BOLA/IDOR). Centralize policy (RBAC/ABAC) in one module that every handler calls, and test it with allow and deny cases.

## 7. Choosing the style

| Need | Prefer |
|---|---|
| Public API, broad clients, caching | REST + OpenAPI |
| Many client shapes, deep graphs, one team owns both sides | GraphQL (add depth/complexity limits, dataloaders, persisted queries) |
| Internal service-to-service, strict schemas, streaming | gRPC |
| TypeScript monorepo, one team | tRPC or shared schema types |

## 8. Performance

HTTP caching (`ETag`, `Cache-Control`), compression, keyset pagination, batching endpoints for chatty clients, dataloaders to kill N+1, select only needed columns, background jobs for slow side effects, connection pooling. Measure p95/p99 per endpoint; budgets come from the fractal budget split.

## 9. Testing the contract

- Contract tests validate responses against the OpenAPI schema; consumer-driven tests (Pact or equivalent) when separate teams consume the API.
- Test matrix per endpoint: happy path, validation failures, unauthenticated, unauthorized (other user's resource), not found, conflict, rate limit, idempotent replay.
- Property-based or fuzz tests on parsers and validators.

## 10. API security checklist (OWASP API Top 10 oriented)

Object-level and function-level authorization; property-level exposure controlled; authentication hardened (lockout/backoff, no credential stuffing paths); resource consumption limited (size, rate, pagination caps, timeouts); SSRF-safe outbound fetches (allow-lists); misconfiguration reviewed (CORS exact origins, headers, debug off); inventory of versions and deprecated endpoints; third-party API responses treated as untrusted input; secrets in a secret manager.
