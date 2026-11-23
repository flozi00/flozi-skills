# flozi-skills

Persönliche Sammlung generisch wiederverwendbarer Skills für [Hermes Agent](https://github.com/NousResearch/hermes-agent).

Dieses Repo ist die **Single Source of Truth**: Skills werden hier entwickelt und gepflegt, dann in die lokale Hermes-Installation synchronisiert.

## Struktur

```
<category>/<skill-name>/
├── SKILL.md          # Pflicht — Frontmatter + Anleitung
├── references/       # optional — vertiefende Doku pro Thema
├── templates/        # optional — Vorlagen/Configs
└── scripts/          # optional — Helper-Scripts
```

Kategorien = die Top-Level-Ordner (z. B. `software-development/`, `productivity/`, `research/`). Eine Kategorie wird beim ersten Skill in ihr angelegt.

## Skills installieren / synchronisieren

```bash
# Alle Skills aus diesem Repo nach ~/.hermes/skills/ kopieren
./install.sh

# Nur eine Kategorie
./install.sh software-development

# Lokale Kopien löschen, die nicht mehr im Repo liegen (Repo gewinnt)
./install.sh --prune
```

Neue Skills sind erst in **neuen Sessions** sichtbar — der Skill-Loader wird beim Session-Start initialisiert.

## Neuen Skill anlegen

1. `TEMPLATE.md` kopieren: `cp TEMPLATE.md <category>/<skill-name>/SKILL.md`
2. Ausfüllen — die wichtigsten Regeln stehen als Kommentare drin.
3. Committen. Fertig.

Kurzregeln fürs Frontmatter:

| Feld | Regel |
|---|---|
| `name` | lowercase, Bindestriche, ≤ 64 Zeichen |
| `description` | **≤ 60 Zeichen**, ein Satz, endet mit `.` — der Skill-Index schneidet bei ~57 chars ab, der Trigger muss in das Fenster passen |
| `version` | Semver, neue Skills starten bei `0.1.0` |
| `platforms` | Nur die OS, auf denen der Skill wirklich läuft |

Body-Ziel: ~100 Zeilen für einfache, ~200 für komplexe Skills. Alles Bulky gehört in `references/`, nicht in die SKILL.md.
