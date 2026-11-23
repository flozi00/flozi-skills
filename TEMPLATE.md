---
name: my-skill-name                # lowercase, Bindestriche, ≤ 64 Zeichen
description: Was der Skill kann, in einem Satz unter 60 Zeichen.
version: 0.1.0
author: Florian Zimmermeister (flozi00)
license: MIT
platforms: [linux, macos, windows] # nur die OS, auf denen er wirklich läuft
metadata:
  hermes:
    tags: [kurze, tags, hier]
    related_skills: []             # nur Skills, die es wirklich gibt
---

# <Skill-Titel>

2-3 Sätze: was der Skill macht, was nicht, und von was er abhängt.

## When to Use

- Konkreter Trigger 1 (wann soll der Agent diesen Skill laden?)
- Konkreter Trigger 2
- **Don't use for:** Gegenfall (wann NICHT)

## Prerequisites

- Env-Vars, installierte Tools, Zugänge — exakt benannt, keine "siehe Doku"-Verweise.

## Procedure

1. Schritt — mit checkbarem Abschlusskriterium ("Exit: X liegt vor").
2. Schritt — Hermes-Tools namentlich nennen (`terminal`, `read_file`, `web_search`, …),
   keine Shell-Wrapper, die Hermes schon abbietet (`grep` → `search_files`, `cat` → `read_file`).
3. Keine maschinenlokalen Pfade (`/Users/florian/...`) — repo-/umgebungsrelative Pfade nutzen.

## Pitfalls

- Bekannte Stolperfallen: was aussieht wie ein Bug, aber keiner ist;
  was silent failt; was man nicht retryen darf.

## Verification

- Wie beweist man, dass der Skill funktioniert hat (echter Tool-Output, Read-back, Exit-Codes).
