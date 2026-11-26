---
name: low-cognitive-load-ui
description: "Design calm UIs: simple by default, powerful on demand."
license: MIT
compatibility: Any UI stack (web, desktop, mobile); principles are platform-neutral.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.2.0"
---

# Low-Cognitive-Load UI

Every extra button costs attention. Design interfaces that a distracted,
overwhelmed, or neurodivergent user (ADHD, autism, low literacy, age-related
decline) can operate without thinking — while power users still reach
everything. The formula: simple by default, powerful on demand, consistent
everywhere, and never rely on memory. Grounded in W3C COGA, WCAG 2.2, and
NN/g progressive-disclosure research.

## When to Use

- Designing or reviewing any UI (web, desktop, mobile).
- Adding a feature, button, or setting to an existing interface.
- **When NOT to use:** pure visual branding; backend-only changes.

## The Audit (in order — stop at the first failing step)

1. **Name the job in the person's words.** One sentence, no product nouns
   ("make this recording sound professional"). If you cannot, the surface
   has no job and the rest of the audit is meaningless.
2. **Count.** Controls per step, distinct strings, primary actions, steps
   after the artifact. Numbers first, opinions second.
3. **Walk the flow as a first-time user.** Keyboard only, reduced motion
   on, sound off, 320 px wide. Every hesitation is a finding.
4. **Read the copy aloud.** Sentence budget, banned words, mechanism
   names, unexplained nouns, raw numbers.
5. **Break it.** Force every error, empty, unavailable and refused state.
   Check cause-then-recovery and that the work survives.
6. **Choose the shape** with the ladder below, then fix the flow before
   the pixels.

## The Shape Ladder

| Situation | Shape |
|---|---|
| More than 3 dependent decisions, or a result that costs money or time | Guided flow: entry, steps, review, run, result |
| 1–3 independent decisions with an immediate result | One screen, one primary action |
| A rare or expert option on an existing object | One disclosure on that object |
| A second surface for the same job | Nothing — fix the existing home |

## Opening an Item from a List

- After opening an item, show its name and the relevant content in the
  current viewport. If it takes time to load, show a named, accessible loading
  state where the detail will appear. Treat a highlighted row with its details
  below unrelated panels as a failed transition.
- Use a focused detail view for editing one item. A split view works for
  frequent switching or comparison when both panes fit. On narrow screens,
  show the detail with a clear return path. Keep unrelated catalogs and
  administrative settings behind their own labeled entrances.
- For a view change, move keyboard focus to the detail heading or the linked
  target. On return, restore the list's search, filters, scroll position and
  focus to the originating item when available. Preserve unsaved edits or
  ask before discarding them.

## The Core Principle: Simple by Default, Powerful on Demand

- The default view shows only the few most important options (NN/g
  progressive disclosure: improves learnability, efficiency, error rate).
- **Reduce simultaneous decisions, never the capability set** — the power
  stays, it just moves behind one deliberate step.
- Advanced or rare features sit behind ONE clearly labeled step
  ("More options", "Advanced") — never more than 2 disclosure levels;
  beyond that users get lost, so chunk instead.
- The progression must be obvious with strong information scent — the
  label says what is inside.
- Power users get keyboard shortcuts, a command palette, bulk actions,
  and API/CLI parity: zero friction for those who know, invisible for
  those who don't.
- Avoid explicit simple/advanced mode toggles unless the gap is huge. If
  used: prominent switch + in-context on-ramp ("You've been using X —
  unlock advanced options?").

## Show Actions People Can Use

- Build everyday menus and toolbars from effective permissions, workspace
  configuration and the current resource state. If an optional feature is
  unavailable and the person cannot enable it from this flow, omit its action
  and explanatory row. Remove empty groups and their triggers. If one action
  remains, consider a directly labeled control when it fits.
- Keep an expected action visible when its prerequisite can be resolved here or
  it is temporarily busy. Explain what the person can do next or show progress.
  For example, keep a form's submit action visible while required fields are
  incomplete.
- If a direct link or an action already in progress is refused, explain the
  reason and any available recovery in context. Keep approvals, risks and stop
  controls visible when they apply. Enforce authorization and availability on
  the server even when the UI omits the control.

## Should This Setting Exist at All?

Ask of every decision, field, toggle, tab and word the flow demands — stop
at the first yes:

| # | Question | If yes |
|---|---|---|
| 1 | Can the platform do it instead of asking? | Ship it. |
| 2 | Can it be derived from a choice the user already made? | Derive it; show read-only where it matters. |
| 3 | Is there one safe default for every deployment? | Default it; expose only as an exception. |
| 4 | Does the runtime already decide it well? | Use the default; keep authorized expert access. |
| 5 | Needed by fewer than 1 in 50 people, and never during daily work? | Advanced/diagnostics, behind a deliberate entry. |
| 6 | None of the above | A real setting: plain name, safe default, one home. |

Only step 6 adds UI. Steps 1–4 simplify the default UI.

## The Rules (each grounded in COGA / WCAG / research)

1. **One primary action per view** — visual weight on the most important
   task; everything else recedes.
2. **One decision per step** — group only independent questions.
3. **Consistency over cleverness** — same function = same look, same
   place, every time (COGA 4.2.3). Muscle memory is accessibility.
4. **Never rely on memory** — multi-step flows show completed/current/
   pending steps, breadcrumbs, a "how I got here" path (COGA 4.2.4).
5. **Clear words** — the most common 1500 words; no jargon, no invented
   terms; explain acronyms within one click (COGA 4.4.1). One noun per
   concept across the whole product; name the outcome, not the mechanism.
6. **Nothing moves unless the user moves it** — no auto-play, no
   blinking, no layout shift on load; subtle, slow animations only
   (COGA 4.5.1).
7. **Controls look like controls** — standard patterns, clear borders,
   large enough targets; non-clickable things never look clickable
   (COGA 4.2.5).
8. **Clear control-to-content relationship** — group controls with what
   they affect; no nested scroll areas (COGA 4.2.6).
9. **Chunk and separate** — logical sections, whitespace/borders as
   dividers, headings that form an outline (COGA 4.3.3).
10. **Errors: prevent, then explain** — inline validation, plain-language
    messages, an obvious recovery path.
11. **Respect attention** — no pop-ups, no auto-advancing carousels, no
    notification spam; timing adjustable (WCAG 2.2.1).
12. **Budgets** — at most 7 ± 2 controls per step, 4 ± 1 unfamiliar items
    per group; first feedback within one second (a silent wait is a
    defect); the flow ends on the goal, not on bookkeeping after it.

## ADHD-Specific

- Minimal menus, clear hierarchy, one focus at a time.
- Visible progress and the next action — support working memory.
- Focus mode / distraction-free view for complex tasks.
- Short forms, chunked steps, save-and-resume.

## Autism-Specific

- Predictability: identical layout every visit, no surprise modals.
- Literal language: no idioms, no sarcasm in UI copy.
- Explicit feedback for every action — what happened, what's next.
- Sensory calm: muted colors, no flashing, optional reduced motion.
- State rules and expectations up front.

## Power-User Paths (keep everything reachable)

- Keyboard shortcuts for every frequent action — the clearest signal of
  respecting power users.
- Command palette that searches all actions.
- Bulk actions, saved views and filters.
- API/CLI parity for everything the UI can do.
- Settings: searchable, grouped, with defaults that work.

## Removing a Setting Without Breaking Anyone

A removal is a behavior change, not a refactor. Do all of these in the
same change:

1. **Keep the stored value readable** — leave the config key in place and
   ignore it, or migrate it; never delete a persisted key an older client
   still reads.
2. **Keep the refusal** — removing a control must not remove the
   server-side check that made it safe; only the knob goes.
3. **Say what happened** — a changelog entry naming what is gone, what
   still works, and what happens to earlier data.
4. **Retire, don't orphan** — existing objects keep a visible, deletable
   row with a plain explanation instead of vanishing or erroring.
5. **Update the guide** — onboarding must stop describing the removed
   control and describe the new default.

## Measurement

- Task success rate and time-on-task with 5 real users beats opinion.
- Count clicks and decisions on the primary path; every added button
  must justify itself (Hick's law: decision time grows with the number
  of visible choices).
- Test with actual neurodivergent users — checklists alone don't prove
  usability.

## Pitfalls

- **Hiding critical features behind disclosure** — discoverability risk;
  critical is not the same as advanced. Safety stays visible in the
  simple view.
- **Three or more disclosure levels** — users get lost; simplify instead.
- **Onboarding that never turns off** — power users resent speed bumps;
  make guidance dismissible and remembered.
- **Icon-only buttons without labels or tooltips.**
- **Nested scroll areas and content that moves on load.**
- **"Clean" minimalism that removes affordances** — unlabeled icons and
  hidden navigation are not simplicity.

## Verification

- [ ] Primary task reachable in ≤ 3 obvious steps from landing
- [ ] One primary action per view; ≤ 7 ± 2 controls per step
- [ ] For list/detail changes, compare the same task before and after with
  pointer and keyboard at narrow and wide widths. Open an existing item from a
  scrolled list. Its identity and relevant content or loading state are visible
  without further scrolling. Returning restores context and protects edits.
- [ ] Check action availability across roles, workspace settings and resource
  states. Try menus with zero or one available action, a temporarily blocked
  action in an active workflow, and a direct attempt that is refused.
- [ ] Same function looks and behaves identically everywhere
- [ ] Multi-step flows show progress and resume after interruption
- [ ] No auto-play, blinking, or layout shift; reduced-motion respected
- [ ] Every power feature reachable via shortcut, palette, or API
- [ ] Every setting passed the "should this exist" ladder
- [ ] Tested with 5 real users, including neurodivergent ones
