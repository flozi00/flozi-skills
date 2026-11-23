# Commit Discipline — Sources

Research basis for the commit-discipline skill (verified 2026-11-23):

- **Trunk Based Development**
  https://trunkbaseddevelopment.com/
  Short-lived branches, committing straight to trunk, release-from-trunk and
  branch-by-abstraction. The primary reference for "every commit deployable,
  WIP on branches, never main".

- **DORA — Trunk-based development**
  https://dora.dev/capabilities/trunk-based-development
  Small batches merged to trunk at least daily, and the measured link to
  delivery performance. Explains the *why* behind the branch policy.

- **DORA — Continuous integration**
  https://dora.dev/capabilities/continuous-integration
  Build/test on every commit, fast feedback, small batches. Defines what CI
  must actually do for a commit to count as "green".

- **DORA — Continuous delivery**
  https://dora.dev/capabilities/continuous-delivery
  Release on demand without impacting users; separates continuous delivery
  from continuous deployment. The bar a commit must not lower.

- **Martin Fowler — Feature Flag (Feature Toggle)**
  https://martinfowler.com/bliki/FeatureFlag.html
  Decoupling deploy from release so incomplete work can land on trunk safely.
  The standard escape hatch when a change cannot be finished in one commit.

- **GoCardless — Zero-downtime Postgres migrations: the hard parts**
  https://gocardless.com/blog/zero-downtime-postgres-migrations-the-hard-parts
  `lock_timeout`, splitting schema changes, avoiding long transactions,
  expand/contract ordering. Field-tested rules for migrations that must ship
  with the code.

- **pgroll — Zero-downtime, reversible schema migrations for Postgres**
  https://github.com/xataio/pgroll
  Serves multiple schema versions simultaneously so old and new app versions
  both work during a rollout — the mechanical version of expand/contract.
