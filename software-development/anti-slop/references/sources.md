# Anti-Slop — Sources

Research basis for the anti-slop skill (verified 2026-11-23):

- **Quegenx/agent-skills — anti-slop-code RULES.md**
  https://github.com/Quegenx/agent-skills/blob/main/skills/anti-ai-slop/anti-slop-code/RULES.md
  Reuse test (input shape / side effects / error behavior / return shape),
  search-before-write procedure, merge-copies procedure.

- **iuliandita/anti-slop (SkillMD)**
  https://skillmd.com/skills/iuliandita/anti-slop
  Three axes (Noise / Lies / Soul), P1–P3 severity, structural duplication
  sweep across sibling dirs, "What NOT to flag".

- **oh-my-codex — ai-slop-cleaner SKILL.md**
  https://github.com/Yeachan-Heo/oh-my-codex/blob/main/plugins/oh-my-codex/skills/ai-slop-cleaner/SKILL.md
  Cleanup-pass ordering (dead code → duplicates → naming/errors → tests),
  behavior lock first, evidence-dense report.

- **Builder.io — How to De-Slop an AI-Generated Codebase**
  https://www.builder.io/blog/de-slop-ai-generated-codebase
  Acceptance condition first ("warning gone" is not acceptance), deletion
  test for abstractions, run the behavior you changed.

- **Anaconda — Deslopping AI Code**
  https://www.anaconda.com/blog/deslopping-ai-code
  Comments say why not what; single-use constants inline; one PR = one
  change; recurring finding → rule/lint/skill entry.

- **GitHub Docs — Review AI-generated code**
  https://docs.github.com/en/copilot/tutorials/review-ai-generated-code
  Functional checks first, AI-specific pitfalls (hallucinated APIs,
  deleted/skipped tests).

- **AI-Generated Smells (arXiv 2605.02741)**
  https://arxiv.org/html/2605.02741
  Volume-Quality Inverse Law: LOC vs. architectural smells ρ ≈ 0.94.

- **AI Daily Check — Clean Code for AI Agents**
  https://aidailycheck.com/learn/clean-code-for-ai-agents
  One checker script in CI + agent instructions; agents are reluctant to
  delete — instruct removal explicitly.
