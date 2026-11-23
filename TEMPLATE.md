---
name: my-skill-name                # MUSS exakt dem Verzeichnisnamen entsprechen; lowercase + Bindestriche, ≤ 64 Zeichen
description: >-                    # WAS der Skill macht + WANN er zu laden ist. Knapp halten (1-2 Sätze).
  Macht X. Use when <Trigger-Situation>.
# YAML-Quoting: Ein einzeiliger (inline) `description:`-Wert, der einen Doppelpunkt
# gefolgt von einem Leerzeichen enthält (z. B. "Agent pipeline: architect plans"),
# MUSS in doppelte Anführungszeichen gesetzt werden — sonst ist das YAML invalid
# und der Skill wird stillschweigend nicht geladen (genau dieser Bug hat 4 Skills
# unsichtbar gemacht). Beispiel: description: "Macht X: Details. Use when Y."
# Alternative: den `>-` Block-Scalar wie oben nutzen — dort sind Doppelpunkte
# unproblematisch, weil der Wert mehrzeilig ist.
license: MIT
compatibility: >-                  # optional: Worauf der Skill angewiesen ist (Tools, Pakete, Netzwerk, OS)
  Benötigt <X>. Läuft auf linux/macos/windows.
metadata:                          # optional: string→string Map (Standard-konform)
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# <Skill-Titel>

2-3 Sätze: was der Skill macht, was er explizit NICHT tut, und wovon er abhängt.

## When to Use

- Konkreter Trigger 1 (die Situation, in der dieser Skill geladen werden soll)
- Konkreter Trigger 2
- **When NOT to use:** Gegenfall (wann der Skill nicht passt)

## Prerequisites

- Env-Vars, installierte Tools, Zugänge — exakt benannt, keine "siehe Doku"-Verweise.

## Workflow

1. Schritt — mit checkbarem Abschlusskriterium ("Erledigt, wenn X vorliegt").
2. Schritt — werkzeug-neutral formulieren: "im Terminal ausführen", "im Web recherchieren",
   "Datei lesen/schreiben" — KEINE agent-spezifischen Toolnamen (die mappt jeder Agent selbst).
3. Keine maschinenlokalen Pfade (`/Users/florian/...`) — relative Pfade oder Platzhalter nutzen.

## Pitfalls

- Bekannte Stolperfallen: was aussieht wie ein Bug, aber keiner ist;
  was silent failt; was man nicht blind retryen darf.

## Verification

- [ ] Checkliste, wie bewiesen wird, dass der Skill funktioniert hat
- [ ] Echter Output/Read-back statt Selbstauskunft ("erledigt" zählt nicht als Beweis)
