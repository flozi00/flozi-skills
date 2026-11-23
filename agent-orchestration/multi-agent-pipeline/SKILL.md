---
name: multi-agent-pipeline
description: Agent pipeline: architect plans, cross-model review, build.
license: MIT
compatibility: >-
  Any multi-agent framework with per-agent model and harness selection
  (Hermes delegate_task, Claude Code Task tool, OpenCode, Droid, custom orchestrators).
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.3.0"
---

# Multi-Agent Pipeline

Every non-trivial task runs as a tiered agent pipeline with a fixed role
hierarchy. The human talks to exactly one agent: the Architect/Orchestrator.
Strong models think, small models do, and no worker ever reviews its own
output. Scale the pipeline to the task — the ROLE SCHEMA is fixed, the
number of instantiated agents scales. A trivial one-tool task collapses to
the orchestrator acting alone; anything spanning multiple files, unknowns,
or quality requirements gets the full pipeline.

## The Hierarchy (fixed roles)

```
Human
  └── Architect / Orchestrator (strong model)   <- single human interface
        ├── Planning agents (strong/mid)
        |     <-> Research agents (small/mid)  -- one team
        ├── Plan Reviewer (different model than planners)
        ├── Coder agents (small/mid)
        |     -> Coder Reviewer (DIFFERENT model + harness than coder)
        ├── Test Agent (small/mid)  -- CI tests after every implementation
        └── Integration / Verification agent (optional)
```

- **One Architect/Orchestrator** — the only agent the human talks to. Owns
  sequencing, convergence, conflict resolution, and the plan document.
- **Every agent has ONE specialized job** and concentrates on it. No role
  bleed: a coder never reviews, a researcher never plans.
- **Planner <-> Researcher team**: planners turn the goal into questions and
  a draft plan; researchers gather evidence per question; planners integrate
  findings into the plan.
- **Plan Reviewer**: attacks the plan for weaknesses, gaps, and wrong
  assumptions — on a DIFFERENT model than the planners wrote it with.
- **Coder + Coder Reviewer pair**: the reviewer MUST run a different model
  than the coder (e.g. Sonnet codes -> DeepSeek reviews critically).
- **Test Agent**: after EVERY implementation, writes the CI tests —
  covering desired AND undesired behavior (see Test Coverage Discipline).
  Runs on a different model than the coder where available (same
  independence principle as the reviewer pair).
- **Different harnesses where available**: Claude models always run in
  Claude Code; DeepSeek runs in OpenCode, Droid, or Hermes — whichever is
  available. Independent toolchains catch independent classes of mistakes.

## Communication Flows

- Human <-> Orchestrator only. Workers never talk to the human.
- Orchestrator -> workers: self-contained briefs (context, verified anchors,
  prescriptive steps, acceptance criteria). Workers -> orchestrator:
  structured verdicts with evidence, not prose summaries.
- Planner <-> Researcher: bidirectional inside the planning team.
- Coder -> Reviewer: reviewer receives the diff + the relevant plan section
  — NOT the coder's reasoning (independent judgment, no anchoring).
- All conflicts and escalations route to the Orchestrator. Never sideways.

## The Loops

1. **Research loop** (planning team): draft plan -> open questions ->
   research tasks -> integrate -> repeat until questions are resolved or
   genuinely need the human.
2. **Plan review loop**: plan -> Plan Reviewer -> weaknesses -> planners
   revise -> re-review. Iterate until no MATERIAL weakness remains
   (cosmetic findings don't block).
3. **Open-question debate**: unresolved decisions get argued autonomously —
   spawn pro/con agents on different models, let them attack each other's
   position, orchestrator picks the best-supported option. Escalate to the
   human only for irreversible/high-stakes calls.
4. **Build loop**: brief -> Coder -> diff -> cross-model Reviewer -> findings
   -> Coder fixes -> re-review. Exit only on reviewer approval.
5. **Test loop**: after reviewer approval -> Test Agent writes CI tests ->
   tests run in CI -> failures route back to the Coder -> fix -> re-run.
   Exit only when CI is green with positive AND negative coverage.
6. **Plan-update loop** (during build): reality diverges from plan -> coder
   reports divergence -> orchestrator has planners update the plan ->
   re-brief affected workers. The plan is a living document, not a contract.

## Test Coverage Discipline

The Test Agent proves two things: that it works, AND that what should not
work does not work. Every implementation gets CI tests covering:

- **Desired behavior** — happy paths, correct usage, edge cases of valid
  input, expected outputs and side effects.
- **Undesired behavior** — invalid/malformed input rejected, unauthorized
  access denied, boundary violations refused, malformed state handled
  gracefully, regressions pinned by test.

Rules:

- Tests assert observable behavior (exit codes, outputs, state), not
  implementation details.
- Every bug found later becomes a regression test before the fix is merged.
- CI is the execution vehicle — a test that never ran in CI does not count.
- Coverage is judged by scenarios, not percentages: each acceptance
  criterion from the brief maps to at least one positive and, where
  meaningful, one negative test.

## Model & Harness Assignment

| Role | Model tier | Harness |
|---|---|---|
| Architect / Orchestrator | Strong (Opus, Fable, GPT Sol, GPT Astra) | native session |
| Planning agents | Strong or mid | native session |
| Research agents | Small/mid (Terra, Sonnet, DeepSeek) | any available |
| Plan Reviewer | Different model than the planners | any available |
| Coder agents | Small/mid | Claude -> Claude Code |
| Coder Reviewer | Different model family than the coder | DeepSeek -> OpenCode / Droid / Hermes (first available) |
| Test Agent | Small/mid, different model than the coder where available | any available; CI runs the tests |

Tier rule: strong models plan and judge; small/mid models code, review,
research, and write. NEVER spawn a strong model as a coding/execution
subagent — quality comes from the plan and the briefs, not the worker tier.

Harness resolution (orca first, direct CLI fallback, headless flags and
pitfalls) lives in the `multi-harness-agents` skill — resolve
role -> model tier -> available harness at spawn time.

## Briefing Discipline (what makes small models work)

Every brief is: self-contained (workers see none of your conversation),
pre-mapped (`file:line` anchors verified by the orchestrator BEFORE
dispatch), prescriptive (what to write, what NOT to touch, which command
proves it), checkable (diff, passing command, output schema — never "make
it good"), and single-axis (one seam per worker).

## Verification Discipline

- A worker's self-report ("done", "fixed") is not a fact. Require a
  verifiable handle — file path, diff, command output — and read it back.
- The Orchestrator owns convergence: merge results, resolve conflicts,
  decide the next wave.
- Escalate to a strong model only for genuine judgment calls, never as a
  retry for failed edits.

## Pitfalls

- **Reviewer on the same model as the coder** — correlated blind spots;
  the entire value of the pair is independence.
- **Reviewer sees the coder's rationale** — anchoring; hand over diff +
  spec only.
- **Plan review skipped under time pressure** — weaknesses surface
  mid-build at ten times the cost.
- **Human pulled into worker conversations** — breaks the single-interface
  rule; route everything through the orchestrator.
- **Endless plan loop** — define "material weakness" up front; stop when
  remaining findings are cosmetic.
- **"Small model produced garbage"** — usually an under-specified brief,
  not a tier problem. Rewrite the brief before upgrading the model.
- **Happy-path-only tests** — a suite that only proves desired behavior
  verifies nothing about abuse, malformed input, or boundary violations;
  that is half a test suite.

## Verification

- [ ] Exactly one orchestrator; the human talked to no one else
- [ ] Every worker had one specialized job and stayed on it
- [ ] Every coder was reviewed by a different model (and harness where available)
- [ ] Every implementation got CI tests covering desired AND undesired behavior
- [ ] CI ran green with positive and negative coverage before convergence
- [ ] Plan went through review loops until no material weakness remained
- [ ] Open questions were debated autonomously, not punted to the human
- [ ] Plan updates during build flowed through planners, not ad-hoc edits
- [ ] Every claimed result verified via a handle, not a self-report
