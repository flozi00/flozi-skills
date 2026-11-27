---
name: slop-cleanup
description: "Clean a sloppy codebase: dead code, duplicates, noise."
license: MIT
compatibility: >-
  Any language; works best with a build/typecheck/lint/test gate and the
  ecosystem's duplicate and dead-code tools.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# Slop Cleanup

Vibe-coded projects accumulate slop faster than features: copy-pasted
helpers that drifted apart, dead branches nobody dares to delete,
commented-out code, phantom abstractions, config nobody sets. This skill is
the bounded campaign that removes it — one proven deletion at a time, with a
ratchet so it does not come back.

`anti-slop` prevents slop while writing. This skill removes what already
exists. The prime directive: **cleanup changes structure, never behavior.**
If behavior changes, it is a bug fix or a feature — not cleanup.

Examples are illustrative; the discipline is language- and stack-neutral.

## When to Use

- A codebase works but is hard to change: duplicates, dead code, noise.
- After a vibe-coding sprint, an agent-built prototype, or a rushed feature.
- Before a major feature or migration — clean the ground first.
- When onboarding reveals "nobody knows what this does".
- **When NOT to use:** behavior is broken (use `bug-hunting-loop`); the
  problem is architecture, not slop (that is a rewrite, not cleanup);
  security review (use `security-review-pentest`).

## The Prime Directive

Cleanup changes structure, never behavior. Every phase below exists to
enforce that:

- A green baseline before the first edit.
- Characterization tests before touching anything load-bearing.
- One smell class per commit, each independently revertible.
- The full gate green after every batch.
- A deletion without a proven reason is a bug waiting to happen.

If you cannot prove a change is behavior-preserving, it does not belong in
the cleanup. Route it to `bug-hunting-loop` (bug) or a feature branch.

## Phase 0 — Baseline

Freeze the current state before touching anything:

1. Run the full gate: build, typecheck, lint, tests. Record the exact
   commands and results in the ledger.
2. If the gate is red: fix or quarantine first. Cleanup on a red baseline
   cannot prove behavior preservation.
3. For critical flows without tests, add characterization tests that pin
   current behavior — including the weird parts. They are the safety net,
   not a quality statement.
4. Work on a dedicated branch. Cleanup never rides along with a feature.

## Phase 1 — Inventory

Map the ground before scanning it:

- Languages, entry points, generated and vendored trees (exclude them),
  test directories, build outputs.
- Half-finished migrations: `git log -S "<distinctive string>"` — they
  strand dead handlers, dead stubs, and live features silently broken
  because their data source was never migrated. Report the broken features
  as bugs, not as cleanup.
- Census: TODO/FIXME/HACK/XXX per directory, commented-out code blocks,
  feature flags and their defaults, env vars read vs. set.
- Write everything into the ledger (`templates/cleanup-ledger.md`).

## Phase 2 — Census the Slop

Enumerate by class; do not sample. Record every candidate with file:line in
the ledger.

| Class | What it looks like | Default verdict |
|---|---|---|
| Dead code | unused exports, orphan files, unreachable branches, stale flags, debug leftovers | delete |
| Duplicates | exact copy-paste, near-duplicates with drift, parallel implementations of one feature | merge |
| Noise | redundant comments, boilerplate, single-use helpers/constants, defensive checks for impossible inputs | delete |
| Lies | hallucinated APIs, swallowed errors, stale deps, tests that ratify the implementation, docs for removed features | fix |
| Soul | over-abstraction, phantom interfaces, config nobody sets, generic names, pass-through wrappers | delete or inline |
| Vibe-specific | TODO graveyards, commented-out code, inconsistent error handling across siblings, cargo-cult try/catch, copy-pasted components with drift, config sprawl, dead feature flags, duplicate upload/auth paths | mixed |

**Find duplicates** with the bundled scanner or the ecosystem tool:

```bash
python3 scripts/dupe_scan.py . --min-block 12
```

It reports normalized line-window matches across files. Exact copy-paste
only — for token-based clone detection across 150+ languages use `jscpd`
or PMD CPD (see Tooling Matrix).

**Find dead code** from both sides — no producer AND no consumer — plus
runtime reachability:

```bash
python3 scripts/orphan_scan.py . --ext .py,.rs,.ts
```

A callee that unconditionally raises or returns early makes all its callers
dead transitively; one such stub can kill several features at once. Prove
deadness from the client/runtime side too: a mounted endpoint proves
nothing connects, a type-only import proves nothing runs.

## Phase 3 — Triage

Every candidate gets exactly one verdict, recorded in the ledger:

- **Delete** — no producer, no consumer, runtime-unreachable. Prove all
  three. Find every consumer first: tests, reexports, registration tables,
  route conventions, scripts, Docker copies, generated inputs, dynamic
  dispatch, reflection, stored entry points. No text match is evidence to
  investigate, not proof of dead code.
- **Merge** — same behavior, different text. Compare semantics before
  consolidating: authorization scope, ownership, tenant/region
  restrictions, privacy and audit coverage, transaction context, lock
  boundaries, cache invalidation, cancellation, error mapping, null
  semantics (missing vs. explicit null vs. empty vs. false vs. zero).
  Keep independent checks where distinct trust boundaries enforce them.
- **Fix** — behavior is wrong or fragile. That is a bug, not cleanup:
  route it to `bug-hunting-loop` with a red test first.
- **Keep** — intentional duplication (integrations likely to diverge),
  framework idioms, security patterns (auth, CORS, validation, rate
  limiting, TLS), project conventions. Record why.
- **Rewrite** — only when the module's shape is the problem, not its
  lines. That is a separate project with its own budget, not a cleanup
  batch.

## Phase 4 — Execute

Safest first, one smell class per commit:

1. **Pure deletions** — dead code, commented-out code, debug leftovers.
2. **Merges** — one definition, repoint every call site, delete the
   duplicates and now-dead imports, re-run the search to confirm a single
   definition remains.
3. **Naming and error-handling cleanup** — honest names, no swallowed
   errors.
4. **Test reinforcement** — replace test theater with behavior tests.

Rules for every batch:

- Preserve the difficult boundaries: authority and refusal order,
  input/storage semantics, effects and atomicity (commit, lock lifetime,
  retry/idempotency), async UI states (overlapping saves, stale responses,
  cancellation). Moving a lookup before an authorization check can
  disclose existence or perform work previously refused.
- Never bundle unrelated refactors. A reviewer must be able to explain the
  batch in one sentence.
- After each batch: full gate green, diff reviewable, behavior identical.
- If a deletion turns out to be load-bearing: revert that commit, record
  it in the ledger as "kept — reason", move on. Do not patch around it.

## Phase 5 — Verify

- [ ] Full gate green with the same commands as the baseline
- [ ] Characterization tests still pass; critical flows walked manually
      where no tests exist
- [ ] Every deletion has a reason in the ledger
- [ ] Diff reviewed for semantic changes, not just line counts
- [ ] No behavior change smuggled in as "cleanup"
- [ ] Residual candidates recorded as unproven, not silently dropped

## Phase 6 — Ratchet

Cleanup without a ratchet is a recurring cost. Every recurring finding
becomes a rule, not a one-off fix:

- Duplicate threshold in CI (`jscpd`/CPD with a baseline).
- Dead-code check (`knip`, `vulture`, `cargo udeps`, `staticcheck`).
- Complexity budget (cyclomatic complexity per function, file size).
- Coverage ratchet (never decrease).
- One checker script — lint + typecheck + dead-code + duplicates + tests —
  exits non-zero on any failure. Baseline existing findings so the rule
  lands green, then fix a manageable group first.

## Tooling Matrix

Use the ecosystem's native tools; they understand entry points, visibility,
and dynamic dispatch better than any generic scanner.

| Ecosystem | Duplicates | Dead code | Complexity | Deps |
|---|---|---|---|---|
| Python | jscpd, CPD | `vulture`, `ruff --select F401,F841` | `radon` | `deptry` |
| Rust | jscpd, CPD | `cargo udeps`, `cargo machete`, `dead_code` lint | `clippy` | `cargo machete` |
| JS/TS | jscpd, CPD | `knip`, `ts-prune` | ESLint complexity | `depcheck` |
| Go | jscpd, CPD | `staticcheck` (U1000), `deadcode` | `gocyclo` | `go mod tidy` |
| Java/Kotlin | jscpd, CPD | PMD, SpotBugs, detekt | PMD | — |
| C# | jscpd, CPD | Roslyn analyzers | — | — |
| Ruby | jscpd, CPD | `debride`, RuboCop `Lint/Useless*` | RuboCop | — |
| PHP | jscpd, CPD | PHPStan, Psalm | — | — |

`jscpd` supports 150+ languages with token-based detection; PMD CPD covers
the major compiled languages. Both find renamed-variable clones that a
line-window scanner cannot.

## Bundled Scanners

- `scripts/dupe_scan.py` — generic normalized line-window duplicate
  detector. `--ext`, `--min-block`, per-extension comment prefixes,
  indentation preserved by default (matters for indentation-significant
  languages). Exact copy-paste only.
- `scripts/orphan_scan.py` — generic orphan-file heuristic: a file whose
  basename is never referenced elsewhere. Configurable entry-point
  patterns. Candidates only — dynamic imports, reflection, and route
  conventions are invisible to it.

## Pitfalls

- **Cleaning inside a feature PR** — goals blur and the cleanup gets half
  done. Run cleanup as its own bounded task.
- **Repository-wide refactor triggered by one lint rule** — scope the
  rule, baseline existing findings, fix a manageable group first.
- **Merging near-twins that only look alike** — compare behavior first;
  sharing the wrong part leaves everyone configuring exceptions.
- **Line-count golf** — a smaller diff is not a quality improvement;
  moving branches to another file changes nothing.
- **Deleting code with dynamic consumers** — reflection, string imports,
  route conventions, stored entry points. Search for the string, not just
  the symbol.
- **Breaking boundaries during cleanup** — reordering an authorization
  check or moving a write outside its transaction is a behavior change.
- **Test theater as reinforcement** — implementation-mirroring tests,
  mock-heavy ceremony, snapshots without semantic assertions.
- **"Warning gone" as acceptance** — state what the program must
  guarantee afterward and test that guarantee.
- **Unbounded campaign** — define the surface and the budget up front;
  record residual candidates instead of sweeping forever.
- **Deleting intentional duplication** — integrations likely to diverge
  are duplicated on purpose. Surface as "consider", never force-merge.
- **Rewriting when deleting would do** — the best cleanup often removes
  code instead of restructuring it.

## Verification

- [ ] Baseline recorded (commands + results) before the first edit
- [ ] Census covers every smell class, not a sample
- [ ] Every candidate has a verdict and a reason in the ledger
- [ ] Deadness proven from producer, consumer, and runtime side
- [ ] Semantic comparison done before every merge
- [ ] One smell class per commit; each independently revertible
- [ ] Full gate green after every batch
- [ ] Boundaries preserved (authority order, transactions, async states)
- [ ] Ratchet landed: recurring findings became rules
- [ ] Residual candidates recorded as unproven

## Related Skills

- `anti-slop` — prevention while writing; this skill is the cleanup counterpart.
- `bug-hunting-loop` — lock behavior with characterization tests before cleanup; route real bugs there.
- `commit-discipline` — one smell class per green, revert-friendly commit.
- `performance-optimization` — when "slop" is actually a latency or resource problem.
- `security-review-pentest` — never delete security patterns; route authz findings there.
- `dependency-upgrades` — stale dependencies are a cleanup target, with the 72h rule.
