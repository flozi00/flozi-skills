---
name: multi-harness-agents
description: Run agents on any harness: orca first, CLI fallback.
license: MIT
compatibility: >-
  macOS/Linux/Windows shells with at least one agent CLI installed
  (orca, claude, codex, opencode, copilot, hermes, droid, pi).
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# Multi-Harness Agents

Run agent workers on whatever harness the environment offers. Orca (the
agent development environment + `orca` CLI) is the preferred orchestration
layer when available; otherwise drive the harness CLIs directly in headless
mode. The core discipline: decouple ROLE (what the agent does) from MODEL
(which model powers it) and HARNESS (which binary runs it). A role brief
never names a harness; the dispatcher resolves role -> model tier ->
available harness at spawn time.

## When to Use

- Spawning coding, review, or test workers in any environment.
- Choosing the harness for a role in the multi-agent pipeline.
- Working on machines where orca is absent but agent CLIs exist.
- **When NOT to use:** a single interactive session with the human —
  no worker spawning, no harness resolution needed.

## Harness Selection Order

1. **Orca available** — `orca status --json` succeeds -> use orca
   orchestration (runs, tasks, supervised workers, decision gates).
   Orchestration is experimental: enable it under Settings -> Experimental
   once per installation.
2. **No orca** — drive the harness CLIs directly (headless modes below).
3. Probe availability before dispatch: `orca status --json` and
   `command -v <cli>` for each candidate. Never assume a harness exists.

## Harness Cheat Sheet (headless invocation)

| Harness | Headless run | Model select | Machine output | Critical notes |
|---|---|---|---|---|
| Claude Code | `claude -p "<prompt>"` | `--model` | `--output-format json` | `--allowedTools` / `--permission-mode` to pre-approve; `--bare` skips skills/hooks/MCP for fast scripted runs (needs `ANTHROPIC_API_KEY`) |
| Codex | `codex exec "<prompt>"` | `--model` / config | `--json` (JSONL) | READ-ONLY sandbox by default — pass `--sandbox workspace-write` for edits; expects a git repo (`--skip-git-repo-check` to waive) |
| OpenCode | `opencode run "<prompt>"` | `--model provider/model` | `--format json` | permissions default to ALLOW; `-p` means `--password`, NOT prompt — the prompt is positional |
| Copilot CLI | `copilot -p "<prompt>"` | `--model` | `--output-format json` | `--allow-tool` / `--deny-tool` fences |
| Hermes | `hermes chat -q "<prompt>"` | config/profile | stdout | tmux for interactive PTY sessions |
| Droid, Pi | check `<cli> --help` | per help | per help | flags move fast; verify on the installed version |

Universal rule: **verify flags with `<cli> --help` on the installed version
before scripting** — these CLIs change monthly, and a stale flag silently
changes semantics (sandbox, permissions, output format).

## Model <-> Harness Pairing

Pair model families with the harness that hosts them natively; keep the
reviewer on a different harness than the coder where possible
(independent toolchains catch independent mistake classes):

- Claude models -> Claude Code.
- GPT/Codex models -> Codex CLI.
- DeepSeek -> OpenCode, Droid, or Hermes — first available.
- Any model -> Hermes (provider-agnostic fallback).
- In orca: per-worker model via `worker-start --model <id> --effort high`
  (supported for Claude, Codex, Muse, Cursor, Antigravity, OpenCode).

## Orca Orchestration Pattern (preferred)

```bash
orca status --json                                   # health gate first
orca orchestration run-create --objective "<objective>" --json
orca orchestration task-create \
  --spec "<task, owner id, allowed files, done criteria>" \
  --task-title "<title>" --json
orca orchestration worker-start --task <taskId> \
  --worktree current --agent codex --json            # or --worktree new-child
orca orchestration check --wait \
  --types worker_done,escalation,question --timeout-ms 30000 --json
```

- Dispatched workers receive a coordinator preamble; they send
  `worker_done` exactly once — even on failure — with `--outcome`,
  including `taskId` and `dispatchId`.
- A timed-out `check --wait` is a progress checkpoint, not a failed worker.
- Never start a second terminal because the first is still starting up —
  wait for idle, then send.
- One owner integrates; reviewers read only; writers get worktrees.

## Direct-CLI Fallback Pattern (no orca)

- Deliver the SAME role brief through the harness's headless mode — the
  brief text does not change, only the transport.
- Isolate writers: `git worktree add` per worker, one writer per worktree,
  merge centrally.
- Collect results via handles (files, diffs, exit codes), never via stdout
  prose; machine-output flags exist for exactly this.
- Sequential shell loops or parallel background jobs both work; keep the
  convergence decision in the orchestrator, not in the shell script.

## Pitfalls

- **Codex read-only default** — without `--sandbox workspace-write` it can
  read the repo but every edit silently does nothing.
- **OpenCode `-p` trap** — it is `--password`; the prompt is positional.
- **Claude Code `--bare` skips project skills/hooks/MCP** — don't expect
  them to load in scripted runs.
- **Orca orchestration is experimental** — gate every session on
  `orca status --json` succeeding first.
- **Assuming flags across versions** — stale flags silently change
  sandbox/permission semantics; `--help` before scripting.
- **Conflating harness and model** — pick them independently:
  role -> model tier -> harness that hosts that model.

## Verification

- [ ] Harness availability probed before dispatch (orca status / command -v)
- [ ] Model-harness pairing matches the pipeline rules; reviewer harness differs from coder where possible
- [ ] Sandbox/permission flags set deliberately — write access only where the role needs it
- [ ] Results collected via handles (files, diffs, exit codes), not stdout prose
