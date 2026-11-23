---
name: performance-optimization
description: "Measure first: latency, memory, DB/Redis round trips."
license: MIT
compatibility: Any stack; needs a profiler, query log/EXPLAIN, and a reproducible workload.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# Performance Optimization

Performance work is measurement work. No optimization without a baseline,
no baseline without a representative workload, no claim without a re-run
under the same conditions. The biggest wins are usually fewer round trips
and less work — not faster code. This skill covers latency, memory, and
especially database/Redis traffic.

Examples use SQL and Redis because round trips dominate most stacks; the
method applies to any datastore, RPC boundary, or runtime.

## When to Use

- Slow workflows, high p95/p99 latency, timeouts.
- Memory growth, GC pressure, OOM kills.
- High database or Redis load; connection pool exhaustion.
- Before scaling hardware (fix the work first, then add capacity).
- **When NOT to use:** correctness bugs (use systematic-debugging); bundle
  size or image slimming (separate concern).

## The Method

1. **Name the symptom, workflow, and hypothesis.** Trace the actual path
   before choosing an optimization: entry point → service → SQL/Redis →
   response. Search for existing caches, batching, and limits before
   adding one.
2. **Establish a reproducible baseline.** Representative dataset, build
   mode (never measure dev builds), hardware, concurrency, duration.
   Choose the metric that explains the symptom: p50/p95/p99 latency, CPU,
   RSS, allocations, query count/plan, pool wait, bytes transferred.
3. **Find the dominant cost.** Profile — flamegraph, query log, EXPLAIN,
   allocation profile. Intuition about bottlenecks is wrong often enough
   to waste days.
4. **Change the smallest attributable part.** Re-measure baseline and
   candidate with the same workload and cache state. Report sample count
   and variance. Keep only demonstrated wins; revert speculative
   complexity with no benefit.

## The Round-Trip Budget (DB and Redis)

Round trips dominate most request latency. Count them per request and
assert the count in tests.

**Database**
- **N+1 detection:** log query count per request; a list endpoint issuing
  one query per row is the classic bug. Fix with a join, a batched IN
  query (chunked), or a dataloader.
- **Bulk writes:** one multi-row INSERT/UPDATE instead of a loop.
- **Indexes:** measure the plan before adding one. Composite index column
  order matters (equality first, range last). Never wrap indexed columns
  in functions. Covering indexes avoid table lookups.
- **Pagination:** keyset (WHERE id > last) over OFFSET for large sets;
  OFFSET scans and discards.
- **Payload:** select only needed columns; avoid SELECT * on wide tables.
- **Pooling:** size the pool to the real concurrency; measure pool wait.
  Never hold a connection or transaction across network calls.

**Redis**
- **Pipeline or MGET** instead of N sequential GETs; one round trip beats
  ten.
- **Cache-aside with explicit contract:** key inputs, scope, capacity,
  TTL, freshness, invalidation. A cache is not an authorization
  authority — re-check permissions on hit when they can change.
- **Don't cache what is cheaper to compute** than to fetch and
  deserialize.
- **Watch serialization cost:** large JSON blobs in Redis can cost more
  than the query they replace.
- **Stampede protection:** lock or single-flight on cold keys; jitter
  TTLs.
- **Bounded storage:** capacity + eviction policy; no unbounded keys.

## Memory

- **Leaks:** listeners, subscriptions, timers, caches without eviction,
  growing maps, closures holding large objects. Measure RSS/heap over
  time under load, not once.
- **Allocations:** avoid per-request large buffers; reuse pools only
  where measurement shows it matters.
- **GC pressure:** object churn and short-lived large allocations;
  measure before tuning GC flags.
- **Bounded everything:** queues, caches, batches, prefetch. Unbounded
  growth is a future OOM.

## Speed

- **Algorithmic wins first:** O(n²) → O(n log n) beats any constant-factor
  tuning.
- **Parallelize independent I/O** with bounded concurrency and
  backpressure; unbounded parallelism just moves the bottleneck.
- **Defer non-critical work:** lazy loading, code splitting, background
  queues — but account for the cost shift (first click, queue latency).
- **Stream large responses** instead of buffering; compress where the
  transfer dominates.
- **Micro-optimization last**, only with a profile proving it matters.

## Benchmark Methodology

- Warm up before measuring; report cold vs. warm separately.
- Same conditions for baseline and candidate: data, cache state, build,
  concurrency.
- Report percentiles, not averages; p99 is where users suffer.
- Sample count and variance stated; a single run proves nothing.
- Never invent a speedup. If measurement is unavailable, say so.

## Regression Guards

- Assert query counts per request in integration tests (low-noise,
  deterministic).
- Keep latency budgets only where they are stable in CI; no brittle
  timing assertions.
- A performance fix without a guard regresses silently.

## Pitfalls

- **Optimizing without a baseline** — you cannot know if it helped.
- **Moving cost instead of removing it** — precompute at write time,
  queue it, cache it: the work still exists somewhere.
- **Measuring dev builds** — unminified, unoptimized, wrong numbers.
- **Averages hiding p99** — the tail is the user experience.
- **Unbounded caches** — a cache without eviction is a memory leak with
  extra steps.
- **Cache as authority** — stale permissions served from cache are a
  security bug.
- **Premature micro-optimization** — readable code that is fast enough
  beats clever code that is 3% faster.

## Verification

- [ ] Symptom, workflow, and hypothesis named
- [ ] Reproducible baseline with representative workload
- [ ] Dominant cost identified by profile, not intuition
- [ ] Query/round-trip count measured before and after
- [ ] Same conditions for baseline and candidate; variance reported
- [ ] Memory bounded: caches, queues, batches have limits
- [ ] Cache contract explicit: key, scope, TTL, invalidation
- [ ] Regression guard added where stable
- [ ] No invented speedups; unmeasured claims labeled

## Related Skills

- `bug-hunting-loop` — when the symptom turns out to be a correctness bug, not a cost problem.
- `commit-discipline` — when each measured win lands as its own green commit.
