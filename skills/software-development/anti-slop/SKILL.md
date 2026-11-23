---
name: anti-slop
description: "Keep AI code clean: no duplication, dead code, or slop."
license: MIT
compatibility: >-
  Any language; works best with a linter, typechecker, dead-code detector,
  and test suite wired into one checker script.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.2.0"
---

# Anti-Slop

AI agents generate code that compiles, passes lint, and still rots the
codebase: near-duplicate helpers, dead code, fallback laundering,
speculative abstraction, hallucinated APIs. This is the standing discipline
for keeping code clean when agents develop autonomously. It complements the
ponytail skills (laziest working solution, up front) — anti-slop keeps the
result clean over time. Apply it DURING coding, not as an afterthought.

## When to Use

- Any implementation task by an agent — the rules apply while writing.
- Reviewing AI-generated changes before merge.
- Cleanup passes on a codebase that already accumulated slop.
- **When NOT to use:** pure correctness/security review (use a code-review
  or security-audit skill); throwaway scripts that will never be maintained.

## The Three Axes of Slop

1. **Noise** — bulk without value: redundant comments, boilerplate,
   single-use constants and helpers, unnecessary annotations.
2. **Lies** — subtly wrong: hallucinated APIs, schema drift, stale deps,
   fallback laundering (swallowing errors to hide uncertainty), tests that
   only ratify the implementation.
3. **Soul** — lacks taste: over-abstraction, generic names, defensive
   overkill for inputs the system cannot receive.

## The Reuse Test (before writing ANY helper, type, or constant)

1. State the behavior you are about to implement in a few words.
2. Derive 3–6 search queries: the proposed name, domain nouns, verbs
   (parse, normalize, resolve, validate, format), synonyms and
   abbreviations (`btn`/`button`, `cfg`/`config`).
3. Search the narrowest useful root first, then broaden (src/, lib/,
   packages/, tests/).
4. Read every close match with its tests and call sites — a near-name is
   not proof of duplication.
5. **Reuse test:** an existing symbol is reusable when it already handles
   the same input shape, side effects, error behavior, and return shape —
   or a small extension preserves its current contract.
6. Prefer reusing, extending, or moving over creating new code.
7. Merging copies is the full move: one focused definition, repoint every
   call site, delete the duplicates and now-dead imports, then re-run the
   search to confirm a single definition remains.

## Before Merging Lookalikes (semantic comparison)

Similar syntax does not establish equivalent behavior. Compare before
consolidating:

- authorization scope, ownership, tenant/region restrictions
- privacy and audit coverage
- transaction context, lock boundaries, cache invalidation
- cancellation, resource cleanup, error mapping
- null semantics: missing vs. explicit null vs. empty vs. false vs. zero

Keep independent checks where distinct trust boundaries enforce them.
Avoid a generic helper with flags that makes each caller harder to
understand — sharing the wrong part leaves everyone configuring exceptions.

## The Deletion Test (before adding ANY abstraction)

- **What existing code will this let us delete?** If every caller keeps
  its old code AND must learn a new wrapper, the abstraction simplified
  nothing.
- No speculative abstraction: no pass-through wrappers, no single-use
  helper layers, no interfaces with one implementation "for later".
- Prefer deleting an unnecessary abstraction over adding one to hide it.
- **Reduced line count is an outcome, never a quota.** Do not minify,
  compress readable statements, or delete useful boundaries to hit a
  number. The clarity test: would a new team member understand this
  faster than the original?

## Cleanup Passes (when slop already exists)

Lock behavior first: regression tests before touching anything. Then one
smell per pass, re-verify after each:

1. **Dead code deletion** — unused code, unreachable branches, stale
   flags, debug leftovers.
2. **Duplicate removal** — merge to one definition, repoint call sites.
3. **Naming / error-handling cleanup** — honest names, no swallowed errors.
4. **Test reinforcement** — replace test theater with behavior tests.

Never bundle unrelated refactors into one change; keep each batch small
enough that a reviewer can explain it.

**Find every consumer before deleting anything:** tests, registration
tables, reexports, route conventions, scripts, Docker copies, generated
inputs, dynamic dispatch, reflection, stored user-tool entrypoints. No
text matches is evidence to investigate, not proof of dead code.

**Preserve the difficult boundaries during cleanup:** authority and
refusal order, input/storage semantics, effects and atomicity (commit,
lock lifetime, retry/idempotency), async UI states (overlapping saves,
stale responses, cancellation). Moving a lookup before an authorization
check can disclose existence or perform work previously refused.

## Quality Gates (before handing work back)

One checker script — linter + typecheck + dead-code detector +
complexity/size check + test suite — exits non-zero on any failure. Run it
in CI and give the agent the command to run it itself. "The warning is
gone" is NOT acceptance: state what the program must guarantee afterward
and test that guarantee.

Tests must assert a protected contract and a real failure. No source-text
checks, line-count checks, implementation-mirroring tests, sleeps, or
duplicate tests manufactured to satisfy a count.

## Rules for Agents Specifically

- **Agents are reluctant to delete.** When you replace code, REMOVE what
  it replaces — never leave it callable "just in case".
- Comments explain WHY, never WHAT; delete comments that repeat the code.
- Single-use constants and helpers stay inline until a second caller needs
  them.
- No defensive checks for inputs the system cannot receive.
- No fallback laundering: fix the root cause or escalate — never swallow
  an error to make a check pass.
- Every line must earn its place: volume correlates with architectural
  decay (LOC vs. architectural smells, ρ ≈ 0.94).
- A recurring finding becomes a lint rule or a line in this skill — not a
  one-off fix.

## What NOT to Flag

- Security patterns (auth, CORS, input validation, rate limiting, TLS) —
  correct even when verbose.
- Framework idioms (Next.js layouts, Django class-based views, Terraform
  module structure).
- Project conventions — the repo's style beats generic "clean code"
  preferences.
- Intentional duplication (integrations likely to diverge) — surface as
  "consider", never force-merge.

## Pitfalls

- **Cleaning up inside a feature PR** — goals blur and the cleanup gets
  half done; run cleanup as its own bounded task.
- **Repository-wide refactor triggered by one lint rule** — scope the
  rule, baseline existing findings, fix a manageable group first.
- **Overcorrecting** — a mistake that happened once does not need a rule;
  a growing ban list makes instruction files unread.
- **Merging near-twins that only look alike** — compare behavior first;
  sharing the wrong part leaves everyone configuring exceptions.
- **Line-count golf** — a smaller diff or file is not a quality
  improvement; moving branches to another file changes nothing.
- **Test theater** — implementation-mirroring tests, mock-heavy ceremony,
  snapshots without semantic assertions.

## Verification

- [ ] Reuse search done before every new helper/type/constant
- [ ] Semantic comparison done before every merge of lookalikes
- [ ] Deletion test answered for every new abstraction
- [ ] Every consumer found before deleting (tests, reexports, dynamic dispatch)
- [ ] No dead code, no swallowed errors, no single-use indirection in the diff
- [ ] Quality gates green (lint, typecheck, dead-code, tests)
- [ ] Acceptance stated as a guarantee, not "warning gone"
- [ ] Cleanup passes separate from feature changes
