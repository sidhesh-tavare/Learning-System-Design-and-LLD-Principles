# Thu 22 Oct 2026 · API notes (own words)

Sources (AlgoMaster, read via Chrome): What Is an API · API Styles · REST API Design.
The "how to answer a system design interview" lesson 404'd on both slugs I tried, so section 7 is from Xu Vol 1 Ch 3, not AlgoMaster.
Index only, no lesson text copied.

---

## 1. What is an API
- API = a defined set of operations + rules one piece of software uses to talk to another. Works local (library, OS) or remote (over a network, usually HTTP).
- Client / server are **roles**, not machines. A server can be a client of another server.
- **Contract** = more than the URL and JSON shape:
  - what the caller sends
  - what fields mean
  - permissions
  - failure behaviour
  - side effects
  - Example: `inStock: true` means "had stock when checked", NOT reserved. A type (bool) doesn't tell you that, the meaning does.
- Contract vs implementation: swap DB for cache behind the same API and callers shouldn't notice, IF the promises (freshness, errors) still hold.
- Money as `amountMinor` (cents), not floats.
- Out-of-contract failures: a request can fail before any HTTP response (can't connect). Client must tell that apart from a 404.

## 2. API styles: pick per communication path, not per system
| Style | Shape | Pick when | Avoid when |
|---|---|---|---|
| REST | resources + HTTP verbs, stateless | public/partner API, CRUD, want HTTP caching | clients need very different nested views |
| GraphQL | client chooses fields, one endpoint | varied client screens, complex relations | few stable endpoints are enough |
| gRPC | call a function, Protobuf over HTTP/2 | internal service-to-service | browser must call directly (needs gRPC-Web + proxy) |
| WebSocket | persistent two-way | chat, games, live dashboards | plain request-response is enough |
| SSE | server pushes one-way over HTTP | order status, notifications, LLM token stream | client also sends frequent messages |
| Webhook | other system calls YOUR URL on an event | payment succeeded, GitHub events | caller needs an immediate result |
| Message-driven | publish event to broker, many consume | fan-out, don't wait on consumers | caller needs response from every consumer |

- REST pain: **over-fetching** (whole user object for a name) and **under-fetching** (3 round trips for one screen). GraphQL fixes those, but costs: query depth/cost limits, N+1 (fix: DataLoader batching), CDN/HTTP caching is harder (single endpoint).
- **gRPC (fixes the ChatGPT report-card gaps)**:
  - `.proto` file = contract. Codegen makes client stubs and server interfaces in any language.
  - Protobuf sends field **numbers + values**, not field names, so payloads are smaller and faster to serialize. (Headers aren't the reason, it still rides on HTTP/2 headers.)
  - HTTP/2 gives **multiplexing** (many calls share one connection) and **streaming** (either side sends a stream). Plus deadlines.
  - Costs: binary is hard to eyeball, browsers can't call it directly, both sides need the .proto.
- Typical e-commerce combo: client → REST/GraphQL → API gateway → gRPC between services; Stripe → webhook; live tracking → WebSocket/SSE.
- **WebSocket at scale:** Alice on server A, Bob on server B → needs a shared pub/sub layer (Redis) to route the message. Plus reconnects, dead-client detection, LB that supports long-lived connections.
- **Webhook receiver rules:** verify signature (HMAC of body with shared secret), reject old timestamps (replay), dedupe by event ID (sender retries → duplicates), return 200 fast and process in a background job.

## 3. REST design cheat sheet
- **Richardson levels:** 0 one endpoint/POST for all · 1 resource URLs · 2 + correct verbs/status codes (where most "REST" APIs live) · 3 + HATEOAS links (rare).
- **URLs:** nouns, plural, lowercase-hyphens, no verbs, no implementation leaks (`/tbl_users`, `.json`). Nest ≤ 2 levels, flatten when child has its own identity. Commands only as sub-resource POST: `POST /invoices/123/void`.
- **Verbs:**
  - GET/HEAD: safe + idempotent
  - PUT: replace, idempotent
  - DELETE: idempotent
  - POST: not idempotent unless you add an **Idempotency-Key**
  - PATCH: depends on the patch (`{"counter":"+1"}` is not idempotent)
  - Idempotent means same final **state**, not same response. First DELETE → 204, retry → 404, fine.
  - Never change state in a GET (prefetchers and crawlers fire GETs).
- **Status codes:**
  - 200 OK · 201 Created (+`Location`) · 202 Accepted (async, return a status URL) · 204 No Content
  - 400 can't parse · 422 parses but fails business rules · 401 not authenticated · 403 authenticated but not allowed · 404 not found (or hiding existence) · 409 state conflict · 412 If-Match failed · 429 rate limit (+`Retry-After`)
  - 500 · 502 bad upstream · 503 overloaded · 504 upstream timeout
  - Retry 5xx with backoff + jitter, and only if idempotent or you hold an idempotency key.
- **Bodies:** client sends only client-controlled fields; server returns the saved resource (id, timestamps, defaults).
- **Pagination:**
  - Offset: simple, jump to page N, but slow on deep pages and drifts when rows are inserted/deleted.
  - Cursor: opaque token, seeks from the last key, stable for feeds/logs, can't jump to page 50.
  - Always: default size, max size, stable sort order.
- **Filter / sort / search:** query params (`?status=pending&sort=-created_at`), consistent names across resources, whitelist sort fields, never raw DB columns. Heavy semantic search → model as its own resource.
- **Caching:** `Cache-Control` (public/private/no-store; `no-cache` ≠ never store, it means revalidate). `ETag` + `If-None-Match` → 304. `ETag` + `If-Match` on writes → 412 if someone else changed it (optimistic concurrency). `Vary` when response depends on a header.
- **Versioning:** additive changes are safe (new endpoint, optional param, new nullable field). Breaking: remove/rename/retype/required field/pagination or auth change. `/v1` path versioning is the easiest default. Define deprecation + sunset.
- **Auth:** authN = who, authZ = what they can do. API keys in the `Authorization` header, never in the URL. JWT: verify signature, issuer, audience, expiry. OAuth2 = delegated authorization, not "login" (OIDC adds login). Resource-level checks live in the service, not only at the gateway.
- **CORS:** only browser JS is affected. `*` can't combine with credentials. Custom request headers must be allowed, custom response headers must be exposed. It is NOT access control.
- **Errors:** RFC 9457 `application/problem+json` (`type, title, status, detail, instance`) + stable app error codes + request ID. Never leak stack traces or SQL.
- **Rate limits:** per IP/user/key/tenant/endpoint/cost-unit. Algorithms: fixed window, sliding window, token bucket, leaky bucket, concurrency limit. 429 + `Retry-After`.

## 4. Protocol decision in one breath
- Chat / multiplayer → WebSocket. Server-only push (order status) → SSE. Internal microservices → gRPC. Public API → REST. Many client shapes → GraphQL. Third party tells you something happened → webhook.
- Answer format for the interview: **pick first, then give the reason, then the cost.**

## 5. Re-do of Thursday recall Q1 (polling)
- 1M users, poll every 2 s → 1,000,000 / 2 = **500K QPS**, not 1M. ChatGPT's report card said 1M QPS: check this. A poll every 2 s means 0.5 requests/s per user.
- Fix: SSE (one-way) or WebSocket (two-way) or long polling → ~0 idle requests; cost is 1M open connections (~10K–100K per server → 10–100 gateway servers) and routing via pub/sub.

## 6. Mistakes / gaps to close
- gRPC: "fewer headers" is the wrong reason. Say: binary Protobuf + HTTP/2 multiplexing + streaming + codegen.
- Still shaky: Kafka consumer groups, partitioning, backpressure, connection limits (Wk 2 MQ).
- Answers rambling: lead with the answer, 1 reason, 1 trade-off.

## 7. Xu 4-step framework (from Vol 1 Ch 3, not AlgoMaster)
| Step | Min (of 45) | Say |
|---|---|---|
| 1. Understand problem, scope | 5 | functional + non-functional reqs, scale (DAU, read:write), what's out of scope |
| 2. High-level design, buy-in | 15 | estimation (QPS, storage), API, data model, boxes + arrows, walk 1–2 flows |
| 3. Deep dive | 15 | 1–2 components the interviewer picks: DB choice, cache, queue, sharding |
| 4. Wrap up | 5–10 | bottlenecks, failure modes, monitoring, scaling next 10x |
- Rule: don't draw before step 1 is done. Don't go silent. Ask, don't assume.
- Skipping step 1 → you design for the wrong scale or wrong features.
