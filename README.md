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
<category>/<skill-name>/
├── SKILL.md          # Pflicht — Frontmatter + Anleitung
├── references/       # optional — vertiefende Doku
├── scripts/          # optional — ausführbare Helper
└── assets/           # optional — Vorlagen, Ressourcen
```

Kategorien = Top-Level-Ordner (z. B. `software-development/`, `productivity/`). Sie dienen nur der Ordnung — flache Agents (Claude Code, Codex, Copilot) bekommen die Skills beim Install ohne Kategorie-Ebene. Der `name` im Frontmatter muss immer exakt dem Skill-Verzeichnisnamen entsprechen.

## Skills installieren / synchronisieren

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
