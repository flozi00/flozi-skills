---
name: commit-discipline
description: "Every commit deployable; WIP on branches, never main."
license: MIT
compatibility: Any VCS and stack; needs a gate (build, typecheck, lint, tests) that CI also runs.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# Commit Discipline

Every commit on the deployable branch is a release candidate: if someone
deploys HEAD right now, nothing breaks. Checkpoints are welcome for
tracking progress — but a checkpoint that cannot pass the gate stays off
the deployable branch. This is the rule that makes "accidentally deployed
an update" a non-event.

## When to Use

- Before every commit and push on a shared or deployable branch.
- Setting up branch, merge, and gate policy for a repo or CI pipeline.
- After an incident caused by a broken or half-finished deploy.
- **When NOT to use:** throwaway local experiments that never leave the
  machine; choosing which dependency version to commit (use
  `dependency-upgrades`).

## The Rule

1. **Every commit on the deployable branch passes the full gate** — build,
   typecheck, lint, tests. No exceptions, no "fix it in the next commit".
2. **Checkpoints are allowed** — commit early and often to track progress,
   but only in a green state on the deployable branch. A checkpoint that
   cannot be green lives on a WIP branch or stays local.
3. **WIP branches are never deployed** — squash/rebase before merge; the
   merge (or squashed commit) is the deployable unit.
4. **Atomic commits** — one logical change; a feature commit includes its
   tests and docs. A commit that only makes sense together with the next
   one is not atomic.
5. **Revert-friendly** — any single commit can be reverted without breaking
   the build. No commit depends on a later commit to compile.
6. **Backward-compatible changes** — schema migrations expand/contract;
   config changes keep old values readable; incomplete features behind
   flags.
7. **Green before push** — run the gate locally or let CI gate the merge;
   never push red to the deployable branch.
8. **Message discipline** — imperative subject; what and why in the body;
   reference the issue/advisory when relevant.

## The Checkpoint Workflow

- **Feature branch:** commit freely, including red states, to track
  progress. Nobody deploys it.
- **Before merge:** rebase/squash into green, atomic commits.
- **Deployable branch:** only green commits; each one deployable.
- **Emergency:** if a red state must land (rare), fix it in the same push —
  never leave it for later.

## Deploy Safety

- **Migrations:** expand (add nullable/new) → deploy → contract (remove
  old) in a later release. Never a destructive migration in the same
  commit as the code that stops using the old shape.
- **Feature flags** for incomplete features; the flag defaults to off.
- **Config:** new keys have safe defaults; removed keys stay readable.
- **Rollback:** the previous release must still work with the new data —
  or the one-way boundary is documented.

## What "Green" Means

- Build succeeds from a clean checkout.
- Typecheck and lint pass.
- The full test suite passes — not just the touched tests.
- The gate is the same one CI runs; no local-only shortcuts.

## Pitfalls

- **"I'll fix it in the next commit"** — the next commit may never come;
  the broken state is deployable.
- **Checkpoint commits on main that don't compile** — exactly the accident
  this rule prevents.
- **Squash-merging a red branch** — the squash hides the red history but
  not the broken state.
- **Destructive migrations bundled with code changes** — rollback breaks.
- **Commit messages that describe the diff, not the intent.**

## Verification

- [ ] Every commit on the deployable branch passes the full gate
- [ ] WIP checkpoints are on branches or local, not on the deployable branch
- [ ] Each commit is atomic and revert-friendly
- [ ] Migrations are expand/contract; config changes backward-compatible
- [ ] Incomplete features behind flags (default off)
- [ ] Commit messages state what and why

## Related Skills

- `bug-hunting-loop` — when "green" needs adversarial tests, not just the existing suite.
- `dependency-upgrades` — when a commit bumps dependencies and must follow the 72 h policy.
