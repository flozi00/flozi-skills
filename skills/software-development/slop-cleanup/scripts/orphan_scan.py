#!/usr/bin/env python3
"""Generic orphan-file heuristic.

A file is an orphan candidate when its basename is never referenced anywhere
else in the tree. Language-agnostic by construction: it looks for the file
stem as an identifier in every other text file, not for import syntax.

Usage:
  python3 orphan_scan.py [root] [--ext .py,.rs,.ts] [--entry "main.*,index.*"]
                         [--skip dir1,dir2] [--limit 100]

Entry patterns are fnmatch globs on the basename that are never orphans by
convention (main.*, index.*, mod.rs, lib.rs, __init__.py, conftest.py,
build.rs, setup.py, manage.py, +page.*, +layout.*, *.test.*, *.spec.*).

Candidates only — verify each before deleting. Dynamic imports, reflection,
route conventions, and string-built paths are invisible to this scan.
"""
import argparse
import fnmatch
import os
import re
from collections import defaultdict

DEFAULT_EXTS = (
    ".py", ".rs", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".svelte",
    ".go", ".java", ".kt", ".kts", ".cs", ".rb", ".php", ".c", ".h",
    ".cc", ".cpp", ".hpp", ".swift", ".scala", ".sh", ".bash", ".sql",
    ".lua", ".ex", ".exs", ".dart", ".vue",
)

DEFAULT_ENTRY = (
    "main.*", "index.*", "mod.rs", "lib.rs", "__init__.py", "__main__.py",
    "conftest.py", "setup.py", "manage.py", "build.rs", "build.gradle*",
    "pom.xml", "Cargo.toml", "package.json", "tsconfig.json",
    "+page.*", "+layout.*", "+error.*", "+server.*",
    "*.test.*", "*.spec.*", "*_test.*", "test_*.py", "*.d.ts",
    "vite.config.*", "next.config.*", "eslint.config.*", ".eslintrc*",
)

DEFAULT_SKIP = {
    ".git", "node_modules", "target", "build", "dist", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", "vendor",
    ".next", ".svelte-kit", "coverage", ".idea", ".vscode",
    ".tox", ".gradle", ".m2", "Pods", "DerivedData",
}

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def stem_variants(path):
    base = os.path.basename(path)
    stem = base.rsplit(".", 1)[0]
    out = {stem}
    if "-" in stem:
        out.add(stem.replace("-", "_"))
        out.add(stem.replace("-", ""))
    return out


def walk_files(root, exts, skip):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in exts:
                yield os.path.join(dirpath, fn)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--ext", default=",".join(DEFAULT_EXTS),
                    help="comma-separated extensions (default: common set)")
    ap.add_argument("--entry", default=",".join(DEFAULT_ENTRY),
                    help="comma-separated fnmatch globs that are never orphans")
    ap.add_argument("--skip", default="",
                    help="extra directory names to skip, comma-separated")
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()

    exts = tuple(e.strip().lower() for e in args.ext.split(",") if e.strip())
    entry = tuple(p.strip() for p in args.entry.split(",") if p.strip())
    skip = DEFAULT_SKIP | {d.strip() for d in args.skip.split(",") if d.strip()}
    root = os.path.abspath(args.root)

    candidates = list(walk_files(root, exts, skip))
    interest = set()
    for path in candidates:
        interest |= stem_variants(path)

    # Reverse index: identifier -> files that mention it. Only identifiers
    # that match a candidate stem are indexed, which keeps memory bounded.
    index = defaultdict(set)
    for path in walk_files(root, exts, skip):
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError:
            continue
        for ident in set(IDENT_RE.findall(text)) & interest:
            index[ident].add(path)

    orphans = []
    for path in candidates:
        base = os.path.basename(path)
        if any(fnmatch.fnmatch(base, pat) for pat in entry):
            continue
        referenced = any(
            index.get(stem, set()) - {path} for stem in stem_variants(path)
        )
        if not referenced:
            orphans.append(path)

    print(f"=== {len(orphans)} orphan candidate(s) out of {len(candidates)} "
          f"files (verify each before deleting) ===")
    for path in sorted(orphans)[:args.limit]:
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                n = sum(1 for _ in f)
        except OSError:
            n = 0
        print(f"  {os.path.relpath(path, root)}  ({n} lines)")
    if len(orphans) > args.limit:
        print(f"  ... and {len(orphans) - args.limit} more")
    if not orphans:
        print("No orphan candidates found.")


if __name__ == "__main__":
    main()
