---
name: database-migrations
description: "Zero-downtime schema changes: expand, migrate, contract."
license: MIT
compatibility: >-
  Any relational database and migration tool. Needs a staging copy of
  production-shaped data and control over the deploy order.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# Database Migrations

A schema change is a distributed-systems problem disguised as a DDL
statement: old code and new code run at the same time, against the same
data, for as long as the rollout takes. This skill covers how to change
schema without downtime, without long locks, and without a rollback that
loses data. It does not cover data modelling or query tuning — only how a
change reaches production safely.

Examples use SQL because DDL is where the danger lives; the rules apply to
any relational engine. Where syntax is engine-specific (online index
builds, `NOT VALID` constraints), the concept is named and one common
dialect is shown.

## When to Use

- Adding, renaming, or dropping a column, table, index, or constraint on a
  table that is live and serving traffic.
- Backfilling or rewriting existing rows.
- Planning a release that changes both schema and the code that reads it.
- Reviewing someone else's migration before it runs against production.
- **When NOT to use:** greenfield schemas with no live data (just write
  the DDL); pure query/index tuning with no schema change (use
  performance-optimization); restoring from backup or disaster recovery.

## The Expand/Contract Pattern

Every breaking schema change is split into three releases, never one:

1. **Expand** — add the new shape *alongside* the old one. New column is
   nullable or has a safe default; new table is additive; new index is
   built online. Old code keeps working untouched.
2. **Migrate** — dual-write or backfill so both shapes hold correct data.
   Deploy code that reads the new shape and writes both.
3. **Contract** — only after every reader and writer uses the new shape,
   remove the old one: drop the column, drop the old index, add the
   `NOT NULL`, tighten the constraint.

The invariant: **at no point does a running version of the code see a
schema it cannot handle.** If a step would break the currently deployed
release, it belongs in a later release.

Rename is the canonical case — it is a drop plus an add, and doing it in
one step breaks every old instance still serving traffic:

```sql
-- Release 1 (expand): new column, old one still authoritative
ALTER TABLE orders ADD COLUMN customer_ref TEXT;
-- Release 2 (migrate): backfill + dual-write in application code
-- Release 3 (contract): old column no longer read anywhere
ALTER TABLE orders DROP COLUMN customer_id;
```

## Zero-Downtime Rules

- **No long locks.** Most engines take an exclusive lock for `ALTER TABLE`
  and hold it for the duration of the rewrite. On a large table that is
  minutes of blocked writes. Prefer metadata-only changes (nullable column
  add, default that the engine stores out-of-line) and split anything that
  rewrites the table into a new table plus a swap.
- **Build indexes online.** A plain `CREATE INDEX` blocks writes for the
  whole build. Use the engine's concurrent/online form — PostgreSQL
  `CREATE INDEX CONCURRENTLY`, MySQL `ALGORITHM=INPLACE, LOCK=NONE`,
  others equivalent. Online builds are slower and can fail leaving an
  invalid index; check for and drop the invalid artifact before retrying.
- **Add constraints without validating.** Add the constraint as not-yet-
  enforced (`NOT VALID` in PostgreSQL, `NOT ENFORCED` elsewhere), then
  validate it in a separate statement that takes only a weak lock. New
  writes are checked immediately; old rows are checked in the background.
- **Never set a volatile default on a big table** in one statement — it
  rewrites every row. Add the column nullable, backfill in batches, then
  set the default for new rows.
- **Keep transactions short.** A migration that holds a transaction open
  while it backfills blocks vacuum/cleanup, bloats the log, and turns one
  slow statement into a stalled system. DDL in its own transaction,
  backfill in many small ones.
- **Set a lock timeout** on the migration session so a queued `ALTER`
  cannot pile every subsequent query up behind it. Fail fast, retry later.
- **Deploy schema before code, and code before cleanup** — see below.

## Ordering: Schema Before Code, Code Before Cleanup

The deploy order is not negotiable, because instances roll one at a time:

1. **Schema first.** The expand migration runs before any new code exists.
   Old code must still work against the expanded schema — that is the test
   of a correct expand step.
2. **Code second.** New code deploys and starts using the new shape. During
   the rollout, old and new instances coexist; both must be correct.
3. **Cleanup last.** The contract migration runs only after the new code is
   fully rolled out and verified — typically the *next* release, not the
   same one.

Corollary: a migration and the code that depends on it are never in the
same deploy if the migration is destructive. If you cannot name the release
in which the old shape stops being read, you are not ready to drop it.

## Rollback Strategy

Decide before writing the migration which of two kinds it is:

- **Reversible** — the down migration restores the previous schema *and*
  the previous release still works with the data as it now stands. Only
  then is a rollback a real option.
- **Forward-only** — the change cannot be undone without data loss (dropped
  column, destructive rewrite, type narrowing). Say so explicitly in the
  migration and in the release notes; the rollback plan is then "roll
  forward with a fix", not "revert".

Rules that hold either way:

- **Code rollback must not require a schema rollback.** Because expand and
  contract are separate releases, reverting the application is safe: the
  expanded schema is a superset the old code ignores.
- **Never write a down migration you have not run.** An untested `down` is
  worse than none — it fails exactly when you need it.
- **Destructive steps are irreversible by definition.** Dropping a column
  or table is a one-way door; take a verified backup or archive the data
  first, and treat the drop as its own release.
- **Data migrations are not schema migrations.** A backfill that overwrote
  values cannot be reverted by DDL; keep the source values until the
  contract step.

## Backfills

A backfill is a long-running write workload against a live table. Treat it
as production traffic, not as a script.

- **Idempotent** — re-running must be safe and produce the same result.
  Write `WHERE new_col IS NULL` (or an equivalent predicate), never
  "update everything again".
- **Resumable** — process in key-ordered batches and record progress, so a
  crash resumes instead of restarting. Keyset pagination
  (`WHERE id > :last ORDER BY id LIMIT :n`) beats `OFFSET`, which degrades
  and skips rows under concurrent writes.
- **Throttled** — sleep between batches, cap rows per batch, and watch
  replication lag and lock waits. A backfill that saturates I/O is an
  outage with a progress bar.
- **Bounded transactions** — one transaction per batch. A single
  transaction over millions of rows holds locks, bloats the log, and
  cannot be cancelled cheaply.
- **Verified at the end** — compare counts and checksums before declaring
  it done (see Verification). "The job exited 0" is not evidence.

```sql
-- one batch, safe to re-run
UPDATE orders
   SET customer_ref = legacy_lookup(customer_id)
 WHERE customer_ref IS NULL
   AND id > :last_id
 ORDER BY id
 LIMIT 1000;
```

## Testing Against Production-Like Data

A migration that is instant on an empty dev database can lock production
for minutes. Test where the data volume and shape are real:

- **Restore a recent production-shaped copy** (anonymised if it contains
  personal data) into staging; run the migration there and measure
  duration and lock behaviour.
- **Check the plan, not just the result.** Confirm the engine takes the
  lock you expect — metadata-only vs. full rewrite — before it runs for
  real.
- **Test the coexistence window.** Run old code and new code against the
  migrated schema simultaneously; that is the state production will be in
  mid-rollout.
- **Test the rollback** if the migration claims to be reversible.
- **Test on the real engine version.** DDL behaviour differs across major
  versions; a staging cluster on a different version proves nothing.

## Versioning

- **Migrations are append-only and ordered.** One directory, one sequence,
  immutable once applied anywhere. Editing an applied migration means
  production and the repository disagree — fix forward with a new one.
- **Every environment applies the same set in the same order.** No
  hand-run SQL in production that is not in the repository.
- **The migration tool records what ran** (a version table or equivalent).
  If it does not, you cannot know whether an environment is current.
- **One logical change per migration**, named for the intent, so a failure
  is attributable and a revert is surgical.
- **Schema version is part of the release contract** — the deploy pipeline
  runs migrations before starting new instances, and refuses to start if
  they fail.

## Pitfalls

- **Destructive change in the same release as the code change** — the
  rollback of the code now needs a rollback of the data, which does not
  exist.
- **`ALTER TABLE` on a large table during peak traffic** — an exclusive
  lock held for the rewrite duration; every write queues behind it.
- **Plain `CREATE INDEX` on a hot table** — blocks writes for the whole
  build; use the online form.
- **One giant transaction** — long locks, log bloat, blocked cleanup, and
  no cheap way to abort.
- **Backfill without a predicate** — re-runs overwrite newer values with
  stale ones.
- **`OFFSET` pagination in a backfill** — skips and duplicates rows when
  the table is being written concurrently.
- **Assuming a dev-sized table proves anything** — duration scales with
  rows; the lock does not care that it was fast locally.
- **Editing an already-applied migration** — environments silently diverge.
- **Untested down migration** — fails precisely when it is needed.
- **Dropping the old column in the same release that stops writing it** —
  old instances still running mid-rollout will write to a column that no
  longer exists.
- **No lock timeout** — a queued migration blocks every query behind it.

## Verification

- [ ] Change is split into expand / migrate / contract across releases
- [ ] Old code still works against the expanded schema (tested, not assumed)
- [ ] No statement takes a long exclusive lock; index builds are online
- [ ] Constraints added unvalidated, then validated separately
- [ ] Backfill is idempotent, resumable, batched, and throttled
- [ ] Migration ran against production-shaped data; duration and locks measured
- [ ] Rollback classified as reversible or forward-only, and stated in the release
- [ ] Down migration executed at least once if it claims to be reversible
- [ ] Row counts and checksums match expectations after the backfill
- [ ] Migration is append-only, ordered, and recorded by the tool
- [ ] Deploy pipeline runs migrations before starting new instances

## Related Skills

- **commit-discipline** — expand/contract is the migration half of "every
  commit deployable"; destructive migrations never share a commit with the
  code that stops using the old shape.
- **performance-optimization** — measuring lock duration, backfill impact,
  and query plans before and after the change.
- **bug-hunting-loop** — adversarial review of the coexistence window:
  what breaks when old and new code run against the same schema.
