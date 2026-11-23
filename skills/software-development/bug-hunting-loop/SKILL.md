---
name: bug-hunting-loop
description: "Hunt bugs adversarially: chains, edge cases, E2E flows."
license: MIT
compatibility: Any language and stack; works best with a test runner, CI, and a way to observe state at boundaries.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# Bug Hunting Loop

Tests prove what you thought of. Bug hunting finds what you didn't. This is
the standing loop for adversarial bug discovery: enumerate the bug classes
that escape normal tests, trace chained scenarios across boundaries, walk
whole end-to-end flows, and turn every found bug into a permanent guard.
Probability is not a filter — reachability is. If a state is reachable, it
is a bug candidate, however unlikely.

Examples are illustrative; the discipline is language- and stack-neutral —
apply it to any runtime, framework, or datastore.

## When to Use

- After a feature is implemented, before release.
- When asked to harden, audit, or "find all the bugs".
- After a bug escaped to production (find its siblings).
- Before a risky migration or refactor.
- **When NOT to use:** reproducing one known bug (use systematic-debugging);
  pure code-style review (use anti-slop).

## The Loop (repeat until the budget is spent)

1. **Map the surface.** Entry points, actors, owned state, irreversible
   effects, invariants. Read callers and consumers, not just the changed
   file.
2. **Enumerate bug classes** with the checklist below — do not sample.
3. **Form hypotheses as causal traces:**
   `precondition → operation A → changed state → operation B → violated
   invariant → consequence`. Name the symbol at each link and the ordering
   that makes it reachable.
4. **Prove with the smallest behavioral test** that goes red on unchanged
   code first. Mock external systems, never the link under test.
5. **Fix at the earliest sound enforcement point**, then check siblings for
   the same class.
6. **Record the escape:** which bug class, why the existing tests missed
   it, and the guard that now fails without the fix.

## The Bug-Class Checklist (enumerate, don't sample)

**Input boundaries**
- absent vs. null vs. empty vs. false vs. zero — when their meaning differs
- boundary values: 0, 1, -1, max, max+1, empty string, whitespace-only
- unicode: combining characters, RTL, emoji, zero-width, normalization
- oversized input, deeply nested structures, duplicate keys
- encoding: UTF-8 vs. latin-1, BOM, invalid byte sequences
- numbers: integer overflow, float precision, rounding, currency units

**State and ordering**
- concurrent writes to the same object; lost updates
- read-modify-write without a lock or compare-and-swap
- stale snapshots; cache invalidation; TTL edges
- partial failure: half-written state, orphaned rows, leaked files
- retry/idempotency: double-submit, replay, at-least-once delivery
- cancellation: work continues after the caller gave up
- restart mid-flow: what survives, what is lost, what is duplicated

**Time**
- timezone conversion, DST transitions, leap seconds, clock skew
- "now" captured once vs. re-read; expiry boundaries (exactly at TTL)
- scheduled jobs overlapping; long-running work crossing midnight/month-end

**Authority and visibility**
- every route reaching the same capability (sibling paths)
- ownership checks on read AND write; admin vs. owner vs. anonymous
- revoked/inactive accounts in an already-open session
- fields leaking through errors, logs, exports, or list endpoints

**Contracts and versions**
- old data read by new code; new data read by old code (rollback)
- stored formats, wire contracts, enum additions, renamed keys
- config drift: stored value vs. default vs. missing

**Resources**
- unbounded growth: caches, queues, listeners, subscriptions, maps
- exhaustion: file descriptors, connections, memory, disk
- rate limits and quotas at the boundary, not after the work

## Chained Scenarios (multi-hop)

Individually correct operations can compose into a violation. For each
candidate chain:

- Follow the real path: trigger → validation/authorization → dispatch →
  background work/stream → persistence/cache → user-visible result.
- Include async callbacks, replay/reconnect, alternate entry points, and
  sibling consumers of shared helpers.
- **Challenge the chain before calling it a bug:** is a guard, transaction,
  cancellation check, or reconciliation step already breaking it? Search
  for counterevidence. Never manufacture a chain by joining unreachable
  states.
- Test the linked operations through their final consequence — helper
  tests that each pass prove nothing about the chain.

## End-to-End Flows

Walk whole user journeys, not just units:

- success path with real persistence across every step
- refusal path: the operation is denied AND no side effect happened
- recovery path: failure mid-flow, retry, resume, rollback
- restart mid-flow: state survives or fails cleanly, never half-applied
- second actor interleaving: another user/session changes state between steps

## Test Suite Reinforcement

- Build an explicit matrix: operation × actor/state × boundary × expected
  result and side effects. Name deliberate exclusions.
- Cover **desired AND undesired behavior**: not only "it works" but "it
  refuses, and nothing forbidden happened".
- Red-to-green evidence: the new test must fail on the pre-fix code for
  the intended reason — a compile error or missing fixture is not a
  reproduction.
- Use barriers, channels, or injected clocks for ordering — never sleeps.
- Assert forbidden side effects stay absent (no outbound call, no write,
  no audit gap), not just the happy result.
- No test theater: no source-text checks, no implementation mirroring, no
  duplicate tests to hit a count.

## Budget and Stopping

- A hunt is a bounded pass, not an endless sweep. Define the surface and
  the budget up front.
- Record residual candidates explicitly as unproven — never claim
  whole-project correctness.
- A class with three or more escapes sharing one cause deserves a
  systematic guard (lint rule, shared test harness), not another point fix.

## Pitfalls

- **Happy-path-only testing** — the refusal and recovery paths are where
  bugs live.
- **Mocking the link under test** — you then test the mock, not the bug.
- **Sleeps instead of synchronization** — flaky tests hide real races.
- **Fixing the symptom** — a guard that hides the final error while
  leaving corrupt state is incomplete.
- **Sampling instead of enumerating** — the sibling path you skipped is
  the one that leaks.
- **Probability as a filter** — "unlikely" is not "unreachable".
- **Unbounded hunts** — a hunt without a budget becomes an endless sweep
  that never ships.

## Verification

- [ ] Surface mapped: entry points, actors, state, invariants
- [ ] Bug-class checklist enumerated, not sampled
- [ ] Every candidate has a causal trace with named symbols
- [ ] Chains challenged for existing guards before being called bugs
- [ ] E2E flows cover success, refusal, recovery, restart
- [ ] New tests fail first on unchanged code, for the intended reason
- [ ] Forbidden side effects asserted absent
- [ ] Every fix has a guard; siblings checked for the same class
- [ ] Residual candidates recorded as unproven

## Related Skills

- `commit-discipline` — when fixes must land as atomic, revert-friendly commits.
- `performance-optimization` — when a suspected bug is actually a latency or resource regression.
- `security-review-pentest` — when a candidate crosses a trust boundary and needs exploitation proof.
