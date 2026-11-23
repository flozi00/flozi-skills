---
name: resilience
description: "Timeouts, retries, breakers, backpressure, degradation."
license: MIT
compatibility: Any stack; needs a way to set timeouts, observe failures, and inject faults in a test environment.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# Resilience

Every dependency fails eventually: a slow database, a flaky third party, a
saturated queue, a network partition. Resilience is the set of mechanisms
that keep a system useful while parts of it are broken — bounded waiting,
bounded retrying, bounded concurrency, and a defined answer when the happy
path is unavailable. It is not "add a retry"; it is a budget you design,
observe, and test.

This skill covers the mechanisms and their failure modes. It does not cover
capacity planning, root-cause debugging of a specific incident, or
performance tuning of healthy paths.

## When to Use

- A service calls another service, database, queue, or third-party API.
- Users see timeouts, 5xx spikes, or cascading failures under load.
- Before a launch or traffic increase that could saturate a dependency.
- When a single slow dependency takes down unrelated features.
- **When NOT to use:** debugging one reproducible failure (use
  systematic-debugging); pure latency work on a healthy path (use
  performance-optimization); missing observability to see failures at all
  (fix that first).

## Timeouts

Every outbound call gets a timeout. No exceptions — a call without one can
block a worker forever and turn a slow dependency into an outage.

- **Set them explicitly** at the client, not only at the load balancer.
  Defaults are often infinite or absurdly long.
- **Budget the chain.** If the request budget is 2s and you make three
  sequential calls, their timeouts must sum to less than 2s, not 2s each.
  Propagate a deadline down the call chain where the stack supports it.
- **Separate connect and read timeouts.** A fast connect with a slow read is
  a different failure than an unreachable host.
- **Timeout implies cancellation.** Abort the in-flight work, release the
  connection, and stop consuming the response. A timeout that leaves the
  operation running is a leak, not a timeout.
- **Pick values from data:** p99 of the dependency plus headroom, not a
  round number. Revisit when the dependency's latency changes.

## Retries

Retries convert transient failures into successes — and, done wrong, into
self-inflicted outages.

- **Only retry idempotent operations**, or make the operation idempotent
  first (idempotency key, dedupe on write). Retrying a non-idempotent write
  duplicates side effects.
- **Retry only retryable errors:** timeouts, connection resets, 429, 502/503/504.
  Never retry 400/401/403/404/422 — the answer will not change.
- **Exponential backoff with jitter.** Base delay, multiplier, cap, and
  full jitter. Without jitter, synchronized clients retry in lockstep and
  hammer a recovering dependency.
- **Cap attempts and total time.** A retry budget (attempts × delay) must
  fit inside the caller's deadline; otherwise the retry outlives the request.
- **Retry budget as a rate, not just per call.** Limit retries to a fraction
  of total traffic (e.g. 10%) so a broad failure cannot multiply load.
- **Respect `Retry-After`** when the server sends it.
- **Retry at one layer.** Retries stacked at gateway, client, and SDK
  multiply: 3 × 3 × 3 = 27 attempts for one user action.

## Circuit Breakers

A breaker stops calling a dependency that is clearly failing, giving it room
to recover and failing fast for callers.

- **Three states:** closed (calls pass), open (calls fail fast), half-open
  (a limited probe decides whether to close).
- **Thresholds are explicit:** failure rate or consecutive failures to trip,
  minimum request volume before evaluating, open duration, and probe count
  in half-open. Tune from observed error rates, not guesses.
- **Count the right failures.** Timeouts and 5xx trip it; business 4xx do not.
- **Half-open is single-flight.** Let a small number of probes through, not
  the full traffic, or you re-trip immediately.
- **Per dependency, per instance class.** One breaker for "the payment API"
  is right; one global breaker for all HTTP calls is not.
- **Emit state changes as events/metrics.** A silently open breaker looks
  like a feature that stopped working.

## Bulkheads

Isolate resources so one failing or slow dependency cannot consume
everything.

- **Separate pools** (connection pools, thread/worker pools, queues) per
  dependency or tenant. A shared pool lets one slow caller starve the rest.
- **Bound each pool** to the concurrency the downstream can actually serve;
  an oversized pool just queues inside the dependency.
- **Isolate by criticality:** interactive traffic must not sit behind batch
  jobs in the same pool.
- **Fail the isolated slice, not the whole.** When the payment pool is
  exhausted, browsing should still work.

## Backpressure

A system that accepts more work than it can process does not get faster; it
gets slower and then falls over.

- **Bounded queues everywhere.** An unbounded queue is a memory leak with a
  delay fuse; it hides overload until the crash.
- **Reject early when full** — return 429/503 with `Retry-After` rather than
  accepting work you cannot finish.
- **Load shedding by priority:** drop or defer low-value work (analytics,
  prefetch, batch) before critical work.
- **Propagate pressure upstream:** slow the producer (pull-based consumers,
  credit/window flow control) instead of buffering.
- **Measure queue depth and wait time**, not just throughput. Rising depth
  at constant throughput is the early warning.
- **Little's Law as a sanity check:** concurrency = arrival rate × latency.
  If your pool is smaller than that product, you are queueing by design.

## Graceful Degradation

Define what the system returns when a dependency is unavailable — before it
happens.

- **Fallbacks per feature:** cached last-known-good response, a reduced
  result, a default, or an explicit "temporarily unavailable" — chosen
  deliberately, never an empty 200 that looks like real data.
- **Serve stale with a marker.** Cached responses need a TTL and an age
  signal so callers can decide; stale data presented as fresh is a
  correctness bug.
- **Degrade features, not the whole page.** Hide the recommendation rail,
  keep checkout working.
- **Never degrade security or correctness:** no skipping authorization,
  no serving another tenant's cache, no silently dropping writes that the
  user believes succeeded.
- **Document the degraded mode** so support and on-call recognize it.

## Health Checks

Health endpoints drive restarts and routing; wrong ones cause outages.

- **Liveness = "is this process wedged?"** It must not check dependencies.
  A liveness probe that fails when the database is down restarts every
  healthy instance and turns a dependency blip into a full outage.
- **Readiness = "should this instance receive traffic?"** It may check
  critical dependencies and warm-up state; failing it removes the instance
  from the load balancer without killing it.
- **Startup probes** for slow boots, so liveness does not kill a process
  that is still initializing.
- **Keep checks cheap and bounded** — a health check that calls five
  services is a new failure mode.
- **Distinguish degraded from dead:** report dependency status separately
  from process health.

## Failure Injection

Resilience you have not tested is a hypothesis.

- **Inject in a controlled environment:** latency, errors, timeouts,
  connection resets, partial responses, and dependency unavailability.
- **Test the mechanisms, not just the outcome:** does the breaker open? does
  the retry respect the budget? does the queue reject at the limit? does the
  fallback return the marked stale value?
- **Run game days / chaos experiments** with a hypothesis, a blast radius,
  and an abort switch. Start small, in staging, then a canary.
- **Verify recovery, not only failure:** the breaker closes, queues drain,
  and latency returns to baseline after the fault is removed.
- **Record findings as regression tests** where the fault can be simulated
  deterministically.

## Pitfalls

- **Retry storms** — many clients retrying without jitter or a budget
  multiply load exactly when the dependency is weakest. The retry becomes
  the outage.
- **Unbounded queues** — they absorb overload silently until memory or
  latency kills the process. Bound them and shed load.
- **Timeouts without cancellation** — the caller gives up, the work keeps
  running, connections and threads leak, and the dependency stays loaded.
- **Liveness probes that check dependencies** — a database blip restarts
  the fleet.
- **Retrying non-idempotent writes** — duplicate charges, double sends,
  duplicated rows.
- **Stacked retries across layers** — multiplicative attempts nobody
  intended.
- **Breakers with no half-open limit** — the probe wave re-trips the
  breaker instantly.
- **Fallbacks that hide failure** — empty 200s and default values that look
  like real data; users and metrics both get lied to.
- **Timeouts longer than the caller's deadline** — the work is wasted and
  the slot is held.
- **Resilience added but never observed** — no metrics on retries, breaker
  state, queue depth, or fallback rate means you cannot tell it is working.

## Verification

- [ ] Every outbound call has an explicit timeout; chain budget ≤ request deadline
- [ ] Timeout aborts the operation (cancellation verified, no leaked work)
- [ ] Retries only on idempotent operations and retryable errors
- [ ] Backoff is exponential with jitter; attempts and total time capped
- [ ] Retry budget bounded as a rate; retries exist at one layer only
- [ ] Breaker thresholds, open duration, and half-open probe limit defined
- [ ] Breaker state changes emit metrics/events
- [ ] Pools and queues are bounded and isolated per dependency/criticality
- [ ] Overload path returns 429/503 with `Retry-After`; low-priority work shed first
- [ ] Fallbacks defined per feature; stale responses carry an age marker
- [ ] Liveness checks no dependencies; readiness reflects traffic-worthiness
- [ ] Failure injection exercised: breaker opens/closes, queue rejects, fallback serves
- [ ] Recovery verified: latency and error rate return to baseline after the fault

## Related Skills

- **performance-optimization** — measure latency and round trips before
  tuning timeouts or pool sizes.
- **observability** — retries, breaker state, queue depth, and fallback rate
  are only useful if they are emitted and alerted on.
- **bug-hunting-loop** — adversarial enumeration of the failure paths these
  mechanisms are supposed to cover.
