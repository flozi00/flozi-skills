#!/usr/bin/env bash
# Install skills from this repo into agent skill directories.
# Usage:
#   ./install.sh                       all skills -> all detected targets
#   ./install.sh --target hermes       only Hermes (~/.hermes/skills/, keeps categories)
#   ./install.sh --target claude       only Claude Code (~/.claude/skills/, flat)
#   ./install.sh --target codex        only OpenAI Codex (~/.agents/skills/, flat)
#   ./install.sh --target copilot      only GitHub Copilot (~/.copilot/skills/, flat)
#   ./install.sh --target all          every target, regardless of detection
#   ./install.sh <category> ...        limit to category dirs
#   ./install.sh --prune ...           also delete installed skill dirs missing in the repo
# Compatible with macOS bash 3.2 (no mapfile, no associative arrays).
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
PRUNE=0
TARGETS=()
CATEGORIES=()
TARGET_ARG=0

for arg in "$@"; do
  case "$arg" in
    --prune) PRUNE=1 ;;
    --target) TARGET_ARG=1 ;;
    -h|--help) sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) if [ "$TARGET_ARG" -eq 1 ]; then TARGETS+=("$arg"); TARGET_ARG=0; else CATEGORIES+=("$arg"); fi ;;
  esac
done

# Discover skills: every dir two levels below skills/ containing a SKILL.md.
SKILLS=()
while IFS= read -r d; do SKILLS+=("$d"); done < <(find "$SRC/skills" -mindepth 3 -maxdepth 3 -name SKILL.md -exec dirname {} \; | sort)

if [ ${#SKILLS[@]} -eq 0 ]; then echo "No skills found in repo."; exit 0; fi

if [ ${#CATEGORIES[@]} -gt 0 ]; then
  FILTERED=()
  for s in "${SKILLS[@]}"; do
    for c in "${CATEGORIES[@]}"; do
      case "$s" in "$SRC/skills/$c/"*) FILTERED+=("$s"); break ;; esac
    done
  done
  SKILLS=("${FILTERED[@]}")
fi

target_base() {
  case "$1" in
    hermes)  echo "$HOME/.hermes/skills" ;;
    claude)  echo "$HOME/.claude/skills" ;;
    codex)   echo "$HOME/.agents/skills" ;;
    copilot) echo "$HOME/.copilot/skills" ;;
    *) return 1 ;;
  esac
}

target_layout() {
  case "$1" in
    hermes) echo "categorized" ;;
    *)      echo "flat" ;;
  esac
}

if [ ${#TARGETS[@]} -eq 0 ]; then
  # Auto-detect: install to every target dir that already exists
  for t in hermes claude codex copilot; do
    b="$(target_base "$t" 2>/dev/null || true)"
    if [ -d "$b" ]; then TARGETS+=("$t"); fi
  done
  if [ ${#TARGETS[@]} -eq 0 ]; then TARGETS=(hermes); fi
fi

# Expand "all" before iterating (the for-loop list is expanded once)
EXPANDED=()
for t in "${TARGETS[@]}"; do
  if [ "$t" = "all" ]; then EXPANDED+=(hermes claude codex copilot); else EXPANDED+=("$t"); fi
done
TARGETS=("${EXPANDED[@]}")

for t in "${TARGETS[@]}"; do
  if ! dest="$(target_base "$t")"; then echo "Unknown target: $t" >&2; exit 1; fi
  layout="$(target_layout "$t")"
  mkdir -p "$dest"
  for s in "${SKILLS[@]}"; do
    name="$(basename "$s")"
    if [ "$layout" = "categorized" ]; then
      cat_dir="$(basename "$(dirname "$s")")"
      target_dir="$dest/$cat_dir/$name"
    else
      target_dir="$dest/$name"
    fi
    mkdir -p "$(dirname "$target_dir")"
    if [ "$PRUNE" -eq 1 ]; then rsync -a --delete "$s/" "$target_dir/"; else rsync -a "$s/" "$target_dir/"; fi
  done
  if [ "$PRUNE" -eq 1 ] && [ "$layout" = "flat" ]; then
    # flat targets: remove installed skills that no longer exist in the repo
    for d in "$dest"/*/; do
      [ -d "$d" ] || continue
      n="$(basename "$d")"
      keep=0
      for s in "${SKILLS[@]}"; do [ "$(basename "$s")" = "$n" ] && keep=1; done
      if [ "$keep" -eq 0 ]; then rm -rf "$d"; echo "pruned: $t/$n"; fi
    done
  fi
  echo "synced ${#SKILLS[@]} skill(s) -> $t ($dest)"
done

echo "Done. New skills usually appear in NEW sessions."
