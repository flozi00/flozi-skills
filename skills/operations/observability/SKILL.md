---
name: observability
description: "Logs, metrics, traces, SLOs: see production clearly."
license: MIT
compatibility: Any stack; needs a log sink, a metrics backend, and ideally a trace collector.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# Observability

You cannot operate what you cannot see. Observability is the ability to ask
new questions about a running system without shipping new code: which
requests are slow, which users are affected, what changed, and whether the
service is meeting its promises. This skill covers the three signals (logs,
metrics, traces), the alerting and SLO layer built on top of them, and the
cost and cardinality discipline that keeps the whole thing affordable.

Examples are illustrative; the discipline is language-, stack-, and
vendor-neutral — apply it to any runtime, datastore, or telemetry backend.

## When to Use

- Standing up monitoring for a new service or a service with none.
- Incidents where you cannot answer "what is broken and for whom".
- Alert fatigue: too many pages, too few that matter.
- Telemetry bill growth from metrics, logs, or trace volume.
- Before a launch, migration, or traffic increase.
- **When NOT to use:** reproducing one known bug (use systematic-debugging);
  pure latency tuning with a working baseline (use performance-optimization).

## The Three Signals

Each signal answers a different question. Use all three; do not force one to
do another's job.

| Signal | Answers | Cost driver |
|---|---|---|
| Logs | What exactly happened in this one case? | Volume, retention |
| Metrics | How much, how often, how fast — in aggregate? | Cardinality, scrape rate |
| Traces | Where did this request spend its time and fail? | Span volume, sampling |

**Rule of thumb:** metrics tell you *that* something is wrong, traces tell
you *where*, logs tell you *why*. An alert should start from a metric or an
SLO, never from a raw log line.

## Logs

- **Structured, not prose.** Emit one machine-parseable record per event
  (key/value or JSON) with stable field names. Never build sentences that a
  human must regex apart.
- **Levels mean something.** Use a small fixed set — debug, info, warn,
  error — and define what each means for this service. `error` means a
  request or job failed and someone may need to act; expected validation
  failures are `info` or `warn`, not `error`. Log at the boundary where the
  failure is decided, once — not at every layer on the way up.
- **Correlation IDs everywhere.** Generate a request/trace ID at the edge,
  propagate it through every call, background job, and queue message, and
  put it on every log line. Without it, multi-service debugging is
  guesswork. Include the tenant/user *identifier* (not personal data) and
  the operation name.
- **Never log secrets or personal data.** No passwords, tokens, API keys,
  session cookies, full card numbers, or raw request bodies that may carry
  them. Redact at the logging boundary, not by hoping callers behave.
  Treat log storage as a lower-trust system than the database.
- **Log the decision, not the noise.** One line per meaningful state
  transition (request finished, job retried, circuit opened) beats a line
  per loop iteration. High-frequency debug logging stays off in production
  or behind a sampled/dynamic switch.
- **Include the fields you will filter on:** timestamp (UTC, ISO-8601),
  level, service, version, correlation ID, duration, outcome, error class.
- **Errors carry context, not stacks alone.** Log the error class, a stable
  message, and the identifiers needed to reproduce; keep stack traces for
  unexpected failures, not for expected control flow.

## Metrics

- **Two framings, pick per service.** RED for request-driven services:
  **R**ate, **E**rrors, **D**uration. USE for resources: **U**tilization,
  **S**aturation, **E**rrors. Do not invent a third taxonomy per team.
- **Percentiles, not averages.** Averages hide the tail, and the tail is
  what users feel. Track p50/p95/p99 (and max where it matters) over a
  window. Never alert on a mean latency.
- **Cardinality is the budget.** Every distinct label combination is a
  separate time series. Never put unbounded values in labels: user IDs,
  request IDs, raw URLs, error messages, timestamps, free-text. Bound them
  to a known set (route template, status class, error code) or drop the
  label. Cardinality explosions are the number-one cause of telemetry cost
  and backend outages.
- **Name and unit conventions.** One naming scheme across services
  (`<subsystem>_<thing>_<unit>`), units in the name (`_seconds`, `_bytes`),
  counters only ever increase, gauges reflect current state.
- **Instrument at boundaries.** Emit metrics where work enters and leaves:
  HTTP/gRPC handlers, queue consumers, outbound client calls, database
  calls, cache hits/misses. Interior helper metrics are usually noise.
- **Business metrics count too.** Signups, orders, payments, queue depth —
  technical health can be green while the product is broken.

## Traces

- **Spans model the request tree.** One root span per request, child spans
  for each meaningful unit of work (handler, outbound call, query, queue
  publish). Name spans by operation, not by code location.
- **Propagate context across every hop.** The trace context must travel in
  headers, message metadata, and job payloads. A broken propagation link
  splits one trace into orphans — the most common tracing failure.
- **Attributes make spans useful.** Record the route template, status,
  duration, retry count, and error flag. Do not record secrets or personal
  data as span attributes; the same redaction rules as logs apply.
- **Sample deliberately.** Head sampling (decide at the root) is cheap and
  predictable; tail sampling (decide after seeing the trace) keeps all
  errors and slow traces while dropping the boring ones. Always keep 100%
  of errors and a slice of successes; never sample so aggressively that
  you cannot reconstruct an incident.
- **Traces are for diagnosis, not for accounting.** Do not bill, count
  users, or drive alerts from sampled trace data.

## SLIs, SLOs, and Error Budgets

- **SLI = a measured ratio of good events to valid events**, defined
  precisely: e.g. "share of HTTP requests that returned non-5xx within
  300 ms, measured at the edge, over 28 days".
- **SLO = the target for that SLI** (e.g. 99.9%). Choose targets from user
  expectation and cost, not from what the system happens to do today.
- **Error budget = 1 − SLO.** It is a spending allowance, not a failure.
  Burn it on launches and risky changes; when it is exhausted, freeze
  feature work and fix reliability. This is the mechanism that makes SLOs
  real instead of decorative.
- **Few SLOs, user-facing.** One to three per service, tied to a user
  journey (availability, latency, freshness, correctness). Internal
  component health is a cause, not an SLO.
- **Measure at the point the user experiences it** — the edge or the
  client — not deep inside a service that may be healthy while the path to
  it is not.

## Alerting

- **Alert on symptoms, not causes.** Page on "users cannot check out" or
  "error budget is burning fast", not on "CPU is 80%". Cause-based alerts
  belong on dashboards, not on phones.
- **SLO burn-rate alerting.** Page on fast burn (a large fraction of the
  budget consumed in a short window) and ticket on slow burn. Multi-window
  (short + long) reduces both false positives and slow detection.
- **Every alert must be actionable.** It names the symptom, the affected
  service, a link to the runbook or dashboard, and the first diagnostic
  step. If the response is "ignore it", delete the alert.
- **Two severities, clearly separated.** Page (a human must act now, at any
  hour) versus ticket (act during business hours). Everything else is a
  dashboard.
- **No alert fatigue.** A page that fires without a real user impact
  trains people to ignore pages. Review alert volume regularly; a noisy
  alert is a bug in the alert, not in the responder.
- **Deduplicate and group.** One incident should produce one page, not
  forty. Group by service and symptom; suppress downstream noise while the
  upstream cause is firing.
- **Test the path.** Alerts, routing, and escalation must be exercised —
  an alert nobody receives is worse than none, because it creates false
  confidence.

## Dashboards

Build for an audience, not for completeness. Three tiers:

- **Service overview (on-call):** RED/USE at a glance, current SLO status
  and error budget remaining, deploy markers, top error classes, saturation.
  Answers "is it broken, and since when?" in under ten seconds.
- **Diagnostic (debugging):** per-endpoint latency percentiles, dependency
  health, queue depth and lag, cache hit rate, database pool and slow
  queries. Answers "where is it broken?".
- **Business (stakeholders):** signups, orders, revenue, active users,
  conversion. No infrastructure jargon.

Rules: one question per dashboard, time range and comparison window
visible, deploy and incident annotations on every chart, no chart without a
unit, and delete panels nobody reads.

## Instrumentation at Boundaries

Instrument once, at the edges, and let the interior stay quiet:

- **Inbound:** every HTTP/gRPC handler, queue consumer, scheduled job —
  rate, errors, duration, and a log line with the correlation ID.
- **Outbound:** every client call to another service, database, cache, or
  third party — latency, error rate, timeout and retry counts. This is
  where dependency problems become visible before they become outages.
- **Async:** queue publish/consume counts, consumer lag, dead-letter
  counts, retry counts. Silent queues are a classic blind spot.
- **Lifecycle:** startup, shutdown, config reload, migration, feature-flag
  change — one structured event each, with the version.
- **Version stamp:** put the build version on every signal. "What changed?"
  is the first question in most incidents, and the answer should be a
  filter, not an archaeology project.

## Cost Control

Telemetry grows faster than traffic if left alone. Treat it as a budget:

- **Cardinality first.** Audit label sets; cap or drop unbounded labels.
  A single high-cardinality label can multiply a metric's cost by orders of
  magnitude.
- **Retention tiers.** High-resolution raw data for days, downsampled
  aggregates for months, cold archive for compliance. Do not keep
  full-resolution traces for a year.
- **Sample what you can afford to lose.** Traces and debug logs are
  sampled; errors, SLO metrics, and audit events are not.
- **Drop known noise at the source** — health checks, readiness probes,
  static asset requests — rather than paying to store and filter them.
- **Review the bill against the value.** If a signal has never answered a
  question in a quarter, it is a candidate for removal.

## Pitfalls

- **Averages instead of percentiles** — the mean is green while p99 users
  time out.
- **Unbounded label values** — user IDs or raw URLs in metrics; cost and
  backend meltdown follow.
- **Logging secrets or personal data** — a compliance incident waiting for
  a log export.
- **Missing correlation IDs** — every multi-service investigation becomes
  manual log archaeology.
- **Broken trace propagation** — orphan spans that never join into a trace.
- **Alerting on causes** — CPU pages that fire during normal batch work and
  teach the team to ignore pages.
- **SLOs nobody uses** — a target with no error budget policy is a
  dashboard decoration.
- **Dashboards built for completeness** — forty panels, no answer.
- **Instrumenting the interior, not the boundaries** — deep helper metrics
  while outbound dependency failures stay invisible.
- **Untested alert routing** — the page that never arrives.
- **Sampling away the errors** — the one trace you needed was dropped.

## Verification

- [ ] Logs are structured with stable field names and a fixed level set
- [ ] Correlation ID generated at the edge and propagated through every hop
- [ ] No secrets or personal data in logs, spans, or metric labels
- [ ] Metrics follow RED or USE; latency tracked as percentiles, not means
- [ ] Every metric label has a bounded value set; cardinality audited
- [ ] Spans cover the request tree; context propagation verified end to end
- [ ] Sampling keeps 100% of errors and slow traces
- [ ] At least one user-facing SLI/SLO per service, with an error budget
      policy that is actually followed
- [ ] Alerts are symptom-based, actionable, grouped, and have a runbook
- [ ] Alert routing and escalation tested end to end
- [ ] Dashboards exist per audience (on-call, diagnostic, business)
- [ ] Instrumentation sits at inbound, outbound, and async boundaries
- [ ] Build version present on every signal
- [ ] Retention tiers and sampling set; telemetry cost reviewed

## Related Skills

- **performance-optimization** — when a latency SLO is missed and you need
  a reproducible baseline and a profile, not more dashboards.
- **bug-hunting-loop** — when telemetry points at a class of failure and
  you need to enumerate and prove the reachable cases.
- **security-review-pentest** — when reviewing what telemetry stores and
  who can read it; logs and traces are an attack surface and a data-leak
  risk of their own.
