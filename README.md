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
