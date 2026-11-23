#!/usr/bin/env python3
"""Validate every skills/<category>/<name>/SKILL.md in this repo.

Stdlib only (no PyYAML): the frontmatter is parsed by hand so that the exact
failure mode that once made four skills invisible is caught -- an unquoted
inline `description` containing ": " is invalid YAML and breaks every loader.

Usage:
    python3 scripts/validate.py [ROOT]

ROOT defaults to the repository root (the parent of this script's directory).
Exit code 1 if any error was found, 0 if there were only warnings.
"""

from __future__ import annotations

import os
import sys

MAX_LINES = 500
DESC_MAX = 60
DESC_WARN = 57
REQUIRED_SECTIONS = ("## When to Use", "## Pitfalls", "## Verification")

QUOTES = ('"', "'")
BLOCK_MARKERS = (">", "|")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.skills = 0

    def error(self, path: str, msg: str) -> None:
        self.errors.append(f"{path}: {msg}")

    def warn(self, path: str, msg: str) -> None:
        self.warnings.append(f"{path}: {msg}")


def split_frontmatter(text: str):
    """Return (frontmatter_lines, body_lines) or (None, None) if malformed."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return lines[1:idx], lines[idx + 1:]
    return None, None


def top_level_fields(fm_lines):
    """Map top-level key -> (inline_value, continuation_lines).

    Only column-0 `key:` lines are treated as fields; indented lines belong to
    the preceding field (block scalars, nested maps).
    """
    fields: dict[str, tuple[str, list[str]]] = {}
    current = None
    for line in fm_lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] not in (" ", "\t"):
            if ":" not in line:
                current = None
                continue
            key, _, value = line.partition(":")
            key = key.strip()
            current = key
            fields[key] = (value.strip(), [])
        elif current is not None:
            fields[current][1].append(line)
    return fields


def strip_comment(value: str) -> str:
    """Drop a trailing ` # comment` that is outside quotes."""
    out = []
    quote = None
    for i, ch in enumerate(value):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in QUOTES:
            quote = ch
            out.append(ch)
            continue
        if ch == "#" and (i == 0 or value[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).strip()


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in QUOTES:
        return value[1:-1]
    return value


def check_description(path: str, raw: str, cont: list[str], rep: Report) -> None:
    value = strip_comment(raw)

    if not value:
        # Block scalar or empty: the marker must be on the next non-blank line.
        first = next((ln.strip() for ln in cont if ln.strip()), "")
        if not first.startswith(BLOCK_MARKERS):
            rep.error(path, "description is empty (expected a quoted string or a >- block scalar)")
            return
        body = " ".join(ln.strip() for ln in cont if ln.strip())
        body = body.lstrip(">|+-").strip()
        length = len(body)
    elif value[0] in QUOTES:
        length = len(unquote(value))
    elif value[0] in BLOCK_MARKERS:
        body = " ".join(ln.strip() for ln in cont if ln.strip())
        length = len(body)
    else:
        # Unquoted inline scalar. A ": " inside it is invalid YAML and is the
        # bug that silently hid skills from discovery.
        if ": " in value or value.endswith(":"):
            rep.error(
                path,
                "description is an unquoted inline value containing ': ' -- "
                "invalid YAML, quote it or use a >- block scalar "
                f"(got: {value!r})",
            )
            return
        length = len(value)

    if length > DESC_MAX:
        rep.error(path, f"description is {length} chars (max {DESC_MAX})")
    elif length > DESC_WARN:
        rep.warn(path, f"description is {length} chars (warn above {DESC_WARN}, max {DESC_MAX})")


def validate_file(path: str, abs_path: str, dirname: str, rep: Report) -> None:
    rep.skills += 1
    try:
        with open(abs_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        rep.error(path, f"cannot read file: {exc}")
        return

    line_count = len(text.splitlines())
    if line_count >= MAX_LINES:
        rep.error(path, f"{line_count} lines (must be < {MAX_LINES})")

    fm_lines, body_lines = split_frontmatter(text)
    if fm_lines is None or body_lines is None:
        rep.error(path, "missing or unterminated YAML frontmatter (--- ... ---)")
        return

    fields = top_level_fields(fm_lines)

    name_raw = fields.get("name", ("", []))[0]
    name = unquote(strip_comment(name_raw))
    if not name:
        rep.error(path, "missing required field 'name'")
    elif name != dirname:
        rep.error(path, f"name {name!r} does not match directory {dirname!r}")

    if "description" not in fields:
        rep.error(path, "missing required field 'description'")
    else:
        raw, cont = fields["description"]
        check_description(path, raw, cont, rep)

    body = "\n".join(body_lines)
    for section in REQUIRED_SECTIONS:
        if section not in body:
            rep.warn(path, f"missing section {section!r}")


def find_skills(root: str) -> list[tuple[str, str]]:
    skills_dir = os.path.join(root, "skills")
    found: list[tuple[str, str]] = []
    if not os.path.isdir(skills_dir):
        return found
    for category in sorted(os.listdir(skills_dir)):
        cat_path = os.path.join(skills_dir, category)
        if not os.path.isdir(cat_path):
            continue
        for name in sorted(os.listdir(cat_path)):
            skill_md = os.path.join(cat_path, name, "SKILL.md")
            if os.path.isfile(skill_md):
                found.append((skill_md, name))
    return found


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        root = os.path.abspath(argv[1])
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    rep = Report()
    skills = find_skills(root)
    if not skills:
        print(f"error: no skills/*/*/SKILL.md found under {root}", file=sys.stderr)
        return 1

    for path, dirname in skills:
        rel = os.path.relpath(path, root)
        validate_file(rel, path, dirname, rep)

    for msg in rep.errors:
        print(f"ERROR   {msg}")
    for msg in rep.warnings:
        print(f"WARNING {msg}")

    print()
    print(f"{rep.skills} skills, {len(rep.errors)} errors, {len(rep.warnings)} warnings")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
