# Cleanup Ledger — <project> — <date>

One ledger per cleanup campaign. It survives context compaction: re-reading
it beats reconstructing state from memory. Update it after every batch.

## Baseline

| Gate | Command | Result |
|---|---|---|
| Build | `<cmd>` | green / red |
| Typecheck | `<cmd>` | green / red |
| Lint | `<cmd>` | green / red |
| Tests | `<cmd>` | green / red |

Characterization tests added: <list, or "none needed">

## Inventory

- Languages / entry points:
- Generated or vendored trees (excluded):
- Half-finished migrations (`git log -S`):
- TODO/FIXME census:
- Feature flags and defaults:
- Env vars read vs. set:

## Census

| # | Class | File:line | Candidate | Verdict | Reason |
|---|---|---|---|---|---|
| 1 | dead code | `src/x.py:40-88` | unused `parse_legacy()` | delete | no producer, no consumer, unreachable |
| 2 | duplicate | `src/a.ts:10-30` / `src/b.ts:44-64` | same retry loop | merge | identical semantics, no boundary difference |
| 3 | noise | `src/c.py:5` | comment repeats code | delete | — |
| 4 | keep | `src/d.ts:1-20` | duplicated auth check | keep | distinct trust boundaries |

## Executed Batches

| Batch | Commit | Smell class | Files | Gate |
|---|---|---|---|---|
| 1 | `<sha>` | pure deletions | 6 | green |
| 2 | `<sha>` | merges | 4 | green |

## Kept With Reason

- `<file:symbol>` — <why it stays>

## Residual Candidates (unproven)

- `<file:symbol>` — <what would prove it>

## Ratchet

- [ ] Duplicate threshold in CI (baseline: N blocks)
- [ ] Dead-code check wired into the checker script
- [ ] Complexity budget
- [ ] Coverage ratchet
