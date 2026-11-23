---
name: api-design
description: "API contracts, versioning, errors, paging, idempotency."
license: MIT
compatibility: >-
  Any stack and protocol (REST, GraphQL, gRPC). Needs a schema/IDL source of
  truth and a way to run contract and boundary tests.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# API Design

An API is a contract with clients you do not control. Design it contract-first,
change it additively, and make every failure mode explicit: stable error codes,
defined pagination, idempotent writes, and limits that are documented rather
than discovered in production. This skill covers the decisions that are
expensive to reverse — naming, versioning, error shapes, pagination,
idempotency, auth boundaries — and applies equally to REST, GraphQL, and gRPC.
It does not cover internal function signatures or UI design.

## When to Use

- Designing a new public or cross-team API surface.
- Adding endpoints, fields, or parameters to an existing API.
- Reviewing an API contract before clients depend on it.
- Debugging client breakage after a change, or planning a deprecation.
- **When NOT to use:** purely internal module interfaces with a single
  in-repo caller; performance tuning of an existing endpoint
  (use performance-optimization); threat modeling of the whole system
  (use security-review-pentest).

## Contract First

- **The schema is the source of truth.** Write the OpenAPI document, GraphQL
  SDL, or `.proto` before the handler. Generate types and stubs from it; never
  hand-maintain a parallel definition that can drift.
- **One artifact, versioned in the repo.** The contract lives next to the code,
  is reviewed in the same change, and is published from CI — not edited in a
  wiki or a vendor dashboard.
- **Contract tests gate the build.** Validate real responses against the schema
  (response validation, not just request validation) so the implementation
  cannot silently diverge.
- **Design for the consumer.** Name things after the domain, not the database
  table. A field called `usr_tbl_stat_cd` is a leak, not an API.

## Versioning and Deprecation

- **Prefer additive evolution over new versions.** Most changes do not need a
  version bump: new optional fields, new endpoints, new enum values clients
  must tolerate. Reserve versioning for breaking changes.
- **Pick one strategy and state it.** URL versioning (`/v1/...`) is explicit,
  cache-friendly, and easy to route; header or media-type versioning
  (`Accept: application/vnd.api+json; version=2`) keeps URLs stable but is
  invisible in logs and proxies. Either is fine — inconsistency is not.
- **Semantic versioning of the contract, not the deploy.** A patch deploy that
  adds an optional field is not a new API version.
- **Deprecation is a process, not a flag.** Announce, document the sunset date,
  emit a `Deprecation`/`Sunset` header (or the protocol equivalent), monitor
  usage per client, and only then remove. Never remove on the same day you
  announce.
- **GraphQL:** deprecate fields with `@deprecated(reason:)`; never reuse a
  removed field name for a different meaning. **gRPC:** reserve removed field
  numbers and names so they cannot be reused.

## Error Shapes

- **One envelope, everywhere.** Every error — validation, auth, rate limit,
  server fault — uses the same structure. Clients should parse errors once.
- **Stable machine-readable codes.** A short, documented `code` string
  (`payment_declined`, `rate_limited`) that never changes meaning. HTTP status
  is the category; the code is the specific reason. Never make clients match on
  human-readable messages.
- **problem+json style** (`application/problem+json`) is a good default:
  `type`, `title`, `status`, `detail`, plus extension members such as `code`,
  `request_id`, and a `errors[]` array of field-level violations.
- **Field-level detail for validation.** Return all violations, not the first
  one, with the offending field path.
- **Never leak internals.** No stack traces, SQL, internal hostnames, or
  upstream provider messages. Log the detail server-side; return a correlation
  id the client can quote.
- **Correct status codes.** 400 malformed, 401 unauthenticated, 403
  unauthorized, 404 absent, 409 conflict, 422 semantically invalid, 429 rate
  limited, 5xx server fault. Do not return 200 with `{"success": false}`.

## Pagination

- **Cursor (keyset) by default** for anything that can grow: stable under
  inserts, no deep-offset scans, O(1) page cost. The cursor is opaque to
  clients — encode the sort key and direction, sign it if it can be tampered
  with.
- **Offset only for small, static, or randomly-accessible sets** where "jump to
  page 7" is a real requirement. Document that offset pages shift when rows are
  inserted or deleted.
- **Always bound the page size.** A default and a hard maximum; reject or clamp
  oversized requests explicitly. An unbounded list endpoint is a DoS vector.
- **Return a consistent envelope:** `items`, `next_cursor` (null at the end),
  and optionally `total` only when it is cheap and honest. A `total` that
  requires a full count on every page is a performance trap.
- **Deterministic ordering.** Pagination without a total order (add a unique
  tiebreaker such as id) duplicates and drops rows.

## Idempotency

- **Writes that create or charge must be idempotent.** Accept an
  `Idempotency-Key` header on POST/PUT; store key → result for a documented
  window; replay the stored response on retry instead of re-executing.
- **Scope the key** to the authenticated principal and the operation, and
  reject reuse with a different payload (409) rather than silently returning
  the old result.
- **Natural idempotency where possible.** PUT with a client-supplied id, or an
  upsert keyed on a business identifier, removes the need for a key store.
- **Retries are the norm, not the exception.** Networks fail after the server
  committed. Design every mutating endpoint assuming the client will retry.
- **GraphQL mutations and gRPC calls** need the same treatment — idempotency is
  a protocol-agnostic concern.

## Rate Limits and Quotas

- **Limit at the edge, per principal and per route class.** Cheap reads and
  expensive writes get different budgets.
- **Advertise the limits.** Return `RateLimit-Limit`, `RateLimit-Remaining`,
  `RateLimit-Reset` (or `Retry-After` on 429) so clients can back off
  correctly.
- **429 with a retry hint, never a silent drop.** Document the algorithm
  (token bucket, sliding window) and the burst allowance.
- **Quotas are a product decision, not just a defense.** State them in the
  contract; changing them is a breaking change for heavy clients.

## Authn and Authz at the Edge

- **Authenticate once at the edge; authorize on every request.** A valid token
  is identity, not permission. Check the specific resource and action
  server-side, every time.
- **Never trust client-supplied identity.** Ignore `user_id` in the body or
  query when the token already carries it; derive the principal from the
  credential.
- **Object-level authorization is the leak.** Verify the caller owns or may
  access *this* record, not just that they hold a valid role. Enumerate the
  denial paths.
- **Scopes and roles are coarse; resource checks are fine.** Combine them.
- **Tokens: short-lived, audience-bound, validated (signature, issuer,
  expiry, audience).** Never accept `alg: none`; never log tokens.
- **CORS, CSRF, and cookies are part of the contract** for browser clients —
  state the allowed origins and credential mode explicitly.

## Naming and Consistency

- **Plural nouns for collections** (`/orders`, `/orders/{id}`), verbs only for
  actions that are not CRUD (`/orders/{id}/cancel`).
- **One casing per protocol:** `snake_case` or `camelCase` in JSON — pick one
  and never mix within a payload. Protobuf uses `snake_case` fields.
- **Consistent field semantics:** timestamps are RFC 3339 UTC with an explicit
  `_at` suffix; ids are opaque strings; money is an integer minor unit plus a
  currency code, never a float.
- **Null vs absent vs empty** must mean the same thing across the API. Document
  which one signals "not set".
- **Enums are open by default.** Clients must tolerate unknown values; servers
  must not reject them on read. Adding an enum value is additive.
- **Boolean names read as predicates** (`is_active`, `has_shipped`), and avoid
  double negatives.

## Backward Compatibility

- **Only additive changes are safe:** new optional request fields, new response
  fields, new endpoints, new enum values (with tolerant clients).
- **Breaking:** removing or renaming a field, tightening validation, changing a
  type, making an optional field required, changing default behavior, changing
  error codes or status for an existing condition.
- **Clients must ignore unknown fields.** Say so in the contract; enforce it in
  your own clients so the rule is real.
- **Never repurpose a field.** A field's meaning is permanent for the life of
  the version; add a new one instead.
- **Test the old client against the new server.** Keep a contract test that
  pins the previous schema and runs it against the current implementation.

## Validation at Boundaries

- **Validate at the edge, once, against the schema.** Reject malformed input
  before it reaches business logic; do not re-validate the same shape in five
  layers.
- **Validate types, ranges, lengths, formats, and required-ness** — and the
  relationships between fields (start before end, currency matches amount).
- **Reject unknown fields on write** where strictness matters (mass-assignment
  protection); tolerate them on read.
- **Bound everything:** string lengths, array sizes, nesting depth, upload
  size, query complexity (GraphQL depth/cost limits).
- **Validation errors are part of the contract** — same envelope, field paths,
  stable codes.

## Documentation

- **The contract is the documentation.** Generated reference from the schema,
  plus a short hand-written guide for auth, pagination, errors, and rate
  limits — the parts a schema cannot express.
- **Every endpoint states:** purpose, auth requirement, idempotency, pagination,
  error codes, and a realistic example request/response.
- **Document the invariants clients rely on:** ordering, eventual consistency
  windows, retry semantics, deprecation policy.
- **Keep examples executable.** Examples that do not run are worse than none;
  generate them from tests where possible.

## Pitfalls

- **Schema drift** — a hand-written doc or client that diverges from the code.
  Generate, do not duplicate.
- **200 with an error body** — breaks every generic client, proxy, and monitor.
- **Matching on error messages** — they change; codes do not.
- **Unbounded list endpoints** — a missing page limit is an outage waiting for
  a large tenant.
- **Offset pagination on a hot table** — duplicates and gaps under concurrent
  writes.
- **Non-idempotent POST behind a retrying client** — double charges, duplicate
  rows.
- **Trusting a client-supplied user id** — the classic authorization bypass.
- **Role check without object check** — valid user, wrong record.
- **Silent breaking change** — tightening validation or changing a default
  looks additive and is not.
- **Version sprawl** — many half-maintained versions because deprecation was
  never finished.
- **Leaking internals in errors** — stack traces and upstream messages are an
  information disclosure.
- **Float money** — rounding errors that surface as accounting bugs.

## Verification

- [ ] Contract (OpenAPI/SDL/proto) exists, is versioned, and is the source of
      generated types
- [ ] Contract tests validate real responses against the schema in CI
- [ ] Versioning strategy stated and applied consistently
- [ ] Deprecation path defined: announcement, sunset header, usage monitoring
- [ ] Single error envelope with stable codes and correct status codes
- [ ] No internal detail (stack traces, SQL, hostnames) in error responses
- [ ] Pagination bounded, ordered deterministically, cursor opaque
- [ ] Mutating endpoints idempotent or key-protected; retry replay verified
- [ ] Rate limits advertised with headers and a documented algorithm
- [ ] Authn at the edge, authz per request and per object; denial paths tested
- [ ] Naming and casing consistent across the whole surface
- [ ] Compatibility check: change is additive, old client tested against new
      server
- [ ] Boundary validation covers types, ranges, sizes, and cross-field rules
- [ ] Docs cover auth, pagination, errors, rate limits, and runnable examples

## Related Skills

- **security-review-pentest** — for the threat model behind authn/authz,
  injection, and boundary hardening.
- **performance-optimization** — for pagination cost, N+1 in list endpoints,
  and payload size.
- **commit-discipline** — contract changes ship in the same deployable commit
  as the code, behind the same gate.
