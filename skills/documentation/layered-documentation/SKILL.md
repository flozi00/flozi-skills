---
name: layered-documentation
description: "3-audience docs + archify diagrams. Use when documenting."
license: MIT
compatibility: >-
  Any repo; archify skill installed for diagram generation
  (works with Claude Code, Codex, Cursor, OpenCode, Hermes).
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# Layered Documentation

Project documentation serves three audiences with three different
questions. Write each audience its own layer and make archify diagrams the
visual backbone. Never mix audiences in one text — a doc for everyone is a
doc for no one.

## When to Use

- Writing or updating project docs (README, docs/, onboarding material).
- After structural code changes (diagram regeneration + L3 refresh).
- **When NOT to use:** inline code comments, commit messages, API
  autodocs — those serve L3 incidentally but are not layered docs.

## The Three Layers

| Layer | Audience | Core question | Form | Home |
|---|---|---|---|---|
| L1 Orientation | Non-technical interested readers | What does this do, and what happens when it runs? | Plain language, no code, no jargon, ≤ 1 page, archify diagram + explainer page | README intro / docs/overview |
| L2 Onboarding | Foreign developers, zero project knowledge | How is it built, and how do I get productive? | Architecture + workflow diagrams, setup that runs, code tour, conventions | docs/onboarding |
| L3 Working reference | Own developers + AI agents | How do I change X without breaking Y? | Exact paths, invariants, gotchas, procedures; terse, current | docs/reference + AGENTS.md / CLAUDE.md |

Layer rules:

- **One fact, one home** — each fact lives in exactly one layer; other
  layers link, never restate.
- Each layer states its audience and a last-verified date.
- L1 is written fresh from the user's perspective — never produced by
  stripping code out of L2 (that reads like a summary, not an explanation).
- L3 is what AI agents load: lists and exact paths over prose, zero
  marketing language.

## Archify Diagrams (the visual backbone)

Install once per environment by telling the agent:

```
Install Archify by reading https://raw.githubusercontent.com/tt-a1i/archify/main/llms.txt
```

Canonical prompts:

- **High-level architecture** (serves L1 simplified + L2):
  "Analyze this repository, then use Archify to create a high-level
  runtime architecture diagram. Show 8–12 core components, one primary
  path, external dependencies, and trust boundaries. Put supporting detail
  in cards instead of adding more edges."
- **Flow deep-dives** (serve L2/L3): workflow and sequence diagrams for the
  primary paths; ERD/class/tree/timeline/waterfall when the question fits.
- **Source-backed mode** (serves L2/L3): repository evidence with source
  references pinned to a commit; regenerate after refactors — the
  architecture diff shows what moved.
- **Explainer page** (serves L1): "Use Archify to answer as one page:
  <question>" — conclusion first, one panel per question, cited sources,
  one self-contained HTML (exportable to PNG/PDF).

Discipline:

- A diagram older than the last structural change is a lie — regenerate.
- Diagrams live in `docs/` beside the layer they serve; L1 embeds the
  simplified view, L2/L3 link the source-backed ones.
- If auto-generated explainer pages add chat noise, set
  `[archify explainer: on-demand]` in the agent's global rules file.

## Update Discipline

- Docs change in the SAME change as the code they describe — a doc PR
  after a code PR is already drift.
- After merge, regenerate affected archify diagrams and refresh the
  last-verified dates.
- Any L3 path that no longer resolves gets fixed on sight.

## Pitfalls

- **One doc for all audiences** — serves none; split by question.
- **Marketing tone in L3** — agents and developers need facts, not adjectives.
- **Diagrams generated once** — they silently lie after the first refactor.
- **L1 written by deleting code from L2** — jargon survives; write fresh.
- **Stale setup instructions in L2** — a setup that was never executed
  does not work; run it before documenting it.

## Verification

- [ ] All three layers exist, each states audience + last-verified date
- [ ] L1 passes the non-programmer test: a reader can retell what it does
- [ ] L2 setup was executed end-to-end, not just written
- [ ] Every L3 path resolves against the current tree
- [ ] Archify diagrams regenerated after the latest structural change

## Related Skills

- `anti-slop` — when the code the docs describe needs a cleanup pass before it is worth documenting.
