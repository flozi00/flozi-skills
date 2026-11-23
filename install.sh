#!/usr/bin/env bash
# Sync skills from this repo into the local Hermes skills directory.
# Usage:
#   ./install.sh              copy all skills (repo -> ~/.hermes/skills/)
#   ./install.sh <category>   copy only one category
#   ./install.sh --prune      also delete local skill dirs that no longer exist in the repo
set -euo pipefail

DEST="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills}"
SRC="$(cd "$(dirname "$0")" && pwd)"
PRUNE=0
CATEGORIES=()

for arg in "$@"; do
  case "$arg" in
    --prune) PRUNE=1 ;;
    -h|--help) echo "Usage: ./install.sh [--prune] [category ...]"; exit 0 ;;
    *) CATEGORIES+=("$arg") ;;
  esac
done

# Every top-level dir that contains at least one SKILL.md is a category.
mapfile -t ALL < <(find "$SRC" -mindepth 2 -maxdepth 2 -name SKILL.md -exec dirname {} \; | xargs -n1 dirname | sort -u)

if [ ${#CATEGORIES[@]} -eq 0 ]; then
  CATEGORIES=("${ALL[@]}")
else
  for c in "${CATEGORIES[@]}"; do
    if [ ! -d "$SRC/$c" ]; then echo "Unknown category: $c" >&2; exit 1; fi
  done
fi

for cat in "${CATEGORIES[@]}"; do
  mkdir -p "$DEST/$cat"
  if [ "$PRUNE" -eq 1 ]; then
    rsync -a --delete "$SRC/$cat/" "$DEST/$cat/"
  else
    rsync -a "$SRC/$cat/" "$DEST/$cat/"
  fi
  echo "synced: $cat"
done

echo "Done. New skills appear in NEW sessions (loader initializes at session start)."
