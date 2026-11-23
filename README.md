# flozi-skills

Persönliche Sammlung generisch wiederverwendbarer **Agent Skills** — nach dem offenen [Agent Skills Standard](https://agentskills.io) (SKILL.md + YAML-Frontmatter), dadurch nutzbar in mehreren Agent-Frameworks, nicht nur einem.

Dieses Repo ist die **Single Source of Truth**: Skills werden hier entwickelt und gepflegt, dann in die jeweiligen Agent-Verzeichnisse synchronisiert.

## Kompatibilität

| Agent | Persönlicher Skills-Pfad | Struktur beim Install |
|---|---|---|
| Hermes Agent | `~/.hermes/skills/` | mit Kategorie-Ordnern |
| Claude Code | `~/.claude/skills/` | flach |
| OpenAI Codex | `~/.agents/skills/` | flach |
| GitHub Copilot | `~/.copilot/skills/` | flach |

Projektbezogen funktionieren die Skills zusätzlich, wenn man sie statt nach `~` in `.claude/skills/` bzw. `.agents/skills/` bzw. `.github/skills/` des jeweiligen Repos legt.

## Struktur

```
skills/<category>/<skill-name>/
├── SKILL.md          # Pflicht — Frontmatter + Anleitung
├── references/       # optional — vertiefende Doku
├── scripts/          # optional — ausführbare Helper
└── assets/           # optional — Vorlagen, Ressourcen
```

Kategorien = Ordner unter `skills/` (z. B. `software-development/`, `design/`). Sie dienen nur der Ordnung — flache Agents (Claude Code, Codex, Copilot) bekommen die Skills beim Install ohne Kategorie-Ebene. Der `name` im Frontmatter muss immer exakt dem Skill-Verzeichnisnamen entsprechen.

Das `skills/`-Layout ist bewusst gewählt: Es ist der Standard-Discovery-Pfad des [`npx skills`](https://github.com/vercel-labs/skills)-CLIs (scannt `skills/` bis 3 Ebenen tief), sodass das Repo direkt per `npx skills add` installierbar ist.

## Skills

| Skill | Kategorie | Beschreibung | Pfad |
|---|---|---|---|
| multi-agent-pipeline | agent-orchestration | Agent pipeline: architect plans, cross-model review, build. | `skills/agent-orchestration/multi-agent-pipeline/SKILL.md` |
| multi-harness-agents | agent-orchestration | Run agents on any harness: orca first, CLI fallback. | `skills/agent-orchestration/multi-harness-agents/SKILL.md` |
| compliance-audit | compliance | DSGVO, ISO 27001, C5, BSI: controls, evidence, gaps. | `skills/compliance/compliance-audit/SKILL.md` |
| low-cognitive-load-ui | design | Design calm UIs: simple by default, powerful on demand. | `skills/design/low-cognitive-load-ui/SKILL.md` |
| layered-documentation | documentation | 3-audience docs + archify diagrams. Use when documenting. | `skills/documentation/layered-documentation/SKILL.md` |
| anti-slop | software-development | Keep AI code clean: no duplication, dead code, or slop. | `skills/software-development/anti-slop/SKILL.md` |
| bug-hunting-loop | software-development | Hunt bugs adversarially: chains, edge cases, E2E flows. | `skills/software-development/bug-hunting-loop/SKILL.md` |
| commit-discipline | software-development | Every commit deployable; WIP on branches, never main. | `skills/software-development/commit-discipline/SKILL.md` |
| dependency-upgrades | software-development | Newest deps ≥72h old; security fixes immediately. | `skills/software-development/dependency-upgrades/SKILL.md` |
| performance-optimization | software-development | Measure first: latency, memory, DB/Redis round trips. | `skills/software-development/performance-optimization/SKILL.md` |
| security-review-pentest | software-development | Security review + pentest: boundaries, authz, injection. | `skills/software-development/security-review-pentest/SKILL.md` |
| data-privacy-engineering | compliance | PII inventory, retention, export/erasure, anonymization. | `skills/compliance/data-privacy-engineering/SKILL.md` |
| observability | operations | Logs, metrics, traces, SLOs: see production clearly. | `skills/operations/observability/SKILL.md` |
| api-design | software-development | API contracts, versioning, errors, paging, idempotency. | `skills/software-development/api-design/SKILL.md` |
| database-migrations | software-development | Zero-downtime schema changes: expand, migrate, contract. | `skills/software-development/database-migrations/SKILL.md` |
| llm-security | software-development | LLM apps: prompt injection, tool safety, output trust. | `skills/software-development/llm-security/SKILL.md` |
| resilience | software-development | Timeouts, retries, breakers, backpressure, degradation. | `skills/software-development/resilience/SKILL.md` |

## Skills installieren / synchronisieren

### Variante A: `npx skills` (empfohlen, agent-übergreifend)

```bash
# Alle Skills aus dem Repo installieren (interaktiv: Skills + Agents wählen)
npx skills add flozi00/flozi-skills

# Nur bestimmte Skills, global, für Hermes + Claude Code
npx skills add flozi00/flozi-skills --skill anti-slop --skill low-cognitive-load-ui -g -a hermes-agent -a claude-code

# Verfügbare Skills im Repo auflisten
npx skills add flozi00/flozi-skills --list

# Updates prüfen und einspielen
npx skills check
npx skills update
```

Unterstützte Agents u. a.: `hermes-agent` (`~/.hermes/skills/`), `claude-code`, `codex`, `github-copilot`, `opencode`, `cursor`, `droid`, `gemini-cli` — volle Liste: [docs/agents.md](https://github.com/vercel-labs/skills/blob/main/docs/agents.md). Private Repos funktionieren mit der bereits konfigurierten Git-Authentifizierung.

### Variante B: `install.sh` (lokal, ohne Node)

```bash
./install.sh                      # alle Skills → alle erkannten Ziele
./install.sh --target hermes      # nur Hermes (~/.hermes/skills/)
./install.sh --target claude      # nur Claude Code (~/.claude/skills/)
./install.sh --target codex       # nur OpenAI Codex (~/.agents/skills/)
./install.sh --target copilot     # nur GitHub Copilot (~/.copilot/skills/)
./install.sh --target all         # explizit alle Ziele
./install.sh software-development # nur eine Kategorie
./install.sh --prune              # lokale Kopien löschen, die es im Repo nicht mehr gibt
```

`--prune` räumt in flachen Zielen (Claude Code, Codex, Copilot) den kompletten Ordner auf; bei Hermes nur innerhalb der Kategorien, die es im Repo gibt — deine übrigen lokalen Hermes-Skills bleiben unangetastet.

Neue Skills sind je nach Agent erst in **neuen Sessions** sichtbar — die meisten Loader initialisieren beim Session-Start.

## Neuen Skill anlegen

1. `TEMPLATE.md` kopieren: `mkdir -p <category>/<skill-name> && cp TEMPLATE.md <category>/<skill-name>/SKILL.md`
2. Ausfüllen — die Regeln stehen als Kommentare drin.
3. Optional validieren: `skills-ref validate <category>/<skill-name>` (Referenz-Validator des Standards).
4. Committen. Fertig.

## Portabilitäts-Regeln

- **Nur Standard-Frontmatter-Felder**: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Agent-spezifische Steuerung (Model, Tool-Restriktionen) gehört nicht ins Frontmatter.
- **Werkzeug-neutral schreiben**: Der Body beschreibt *Fähigkeiten* („im Terminal ausführen", „im Web recherchieren", „Dateien lesen/schreiben"), keine agent-spezifischen Toolnamen. Jeder Agent mappt das auf seine eigenen Tools.
- **`description` = WAS + WANN**: „Macht X. Use when Y." — Agents entdecken Skills ausschließlich über die Description. Knapp halten (1–2 Sätze), auch wenn der Standard 1024 Zeichen erlaubt: manche Agents (z. B. Hermes) zeigen im Skill-Index nur die ersten ~60 Zeichen.
- **SKILL.md unter 500 Zeilen**; alles Detailreiche in `references/`, alles Ausführbare in `scripts/` (Progressive Disclosure).
