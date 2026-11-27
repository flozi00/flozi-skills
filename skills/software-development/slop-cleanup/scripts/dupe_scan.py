#!/usr/bin/env python3
"""Generic cross-file duplicate-block detector.

Finds normalized line-blocks that repeat across 2+ files. Language-agnostic
by construction: it hashes line windows, not syntax trees.

Usage:
  python3 dupe_scan.py [root] [--ext .py,.rs,.ts] [--min-block 12]
                       [--strip-indent] [--skip dir1,dir2] [--limit 40]

Comment prefixes are per extension (COMMENT_PREFIXES); unknown extensions
strip nothing. Indentation is preserved by default — it matters for
indentation-significant languages. Pass --strip-indent for languages where
nesting depth is irrelevant.

This finds exact copy-paste only. For token-based clone detection across
150+ languages use jscpd or PMD CPD.
"""
import argparse
import hashlib
import os
from collections import defaultdict

DEFAULT_EXTS = (
    ".py", ".rs", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".svelte",
    ".go", ".java", ".kt", ".kts", ".cs", ".rb", ".php", ".c", ".h",
    ".cc", ".cpp", ".hpp", ".swift", ".scala", ".sh", ".bash", ".sql",
    ".lua", ".ex", ".exs", ".dart", ".vue",
)

# Per-extension comment prefixes. Deliberately NOT a global "#" rule:
# Rust and PHP attributes (#[derive(...)], #[Route(...)]) start with "#"
# and must survive normalization.
COMMENT_PREFIXES = {
    ".py": ("#",), ".rb": ("#",), ".sh": ("#",), ".bash": ("#",),
    ".ex": ("#",), ".exs": ("#",),
    ".rs": ("//",), ".ts": ("//",), ".tsx": ("//",), ".js": ("//",),
    ".jsx": ("//",), ".mjs": ("//",), ".cjs": ("//",),
    ".svelte": ("//", "<!--"), ".vue": ("//", "<!--"),
    ".go": ("//",), ".java": ("//",), ".kt": ("//",), ".kts": ("//",),
    ".cs": ("//",), ".php": ("//", "#"), ".c": ("//",), ".h": ("//",),
    ".cc": ("//",), ".cpp": ("//",), ".hpp": ("//",), ".swift": ("//",),
    ".scala": ("//",), ".dart": ("//",),
    ".sql": ("--",), ".lua": ("--",),
}

DEFAULT_SKIP = {
    ".git", "node_modules", "target", "build", "dist", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", "vendor",
    ".next", ".svelte-kit", "coverage", ".idea", ".vscode",
    ".tox", ".gradle", ".m2", "Pods", "DerivedData",
}


def is_comment(s, prefixes):
    if not prefixes:
        return False
    if s.startswith("#["):  # Rust / PHP attribute, not a comment
        return False
    if s.startswith(prefixes):
        return True
    # block-comment continuations: "* text", "*", "*/"
    if s in ("*", "*/") or s.startswith("* "):
        return True
    return False


def normalize(line, prefixes, strip_indent):
    s = line.rstrip("\n").rstrip()
    if strip_indent:
        s = s.strip()
    if not s.strip():
        return ""
    if is_comment(s.strip(), prefixes):
        return ""
    return s


def merge_ranges(lines):
    out = []
    for ln in sorted(set(lines)):
        if out and ln == out[-1][1] + 1:
            out[-1][1] = ln
        else:
            out.append([ln, ln])
    return out


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--ext", default=",".join(DEFAULT_EXTS),
                    help="comma-separated extensions (default: common set)")
    ap.add_argument("--min-block", type=int, default=12,
                    help="minimum normalized lines per block (default: 12)")
    ap.add_argument("--strip-indent", action="store_true",
                    help="ignore leading indentation (default: preserve)")
    ap.add_argument("--skip", default="",
                    help="extra directory names to skip, comma-separated")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    exts = tuple(e.strip().lower() for e in args.ext.split(",") if e.strip())
    skip = DEFAULT_SKIP | {d.strip() for d in args.skip.split(",") if d.strip()}
    root = os.path.abspath(args.root)

    file_lines = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in exts:
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    raw = f.readlines()
            except OSError:
                continue
            prefixes = COMMENT_PREFIXES.get(ext, ())
            file_lines[path] = [
                normalize(l, prefixes, args.strip_indent) for l in raw
            ]

    windows = defaultdict(set)  # window hash -> {(file, start_index)}
    for path, normed in file_lines.items():
        for i in range(len(normed) - args.min_block + 1):
            window = normed[i:i + args.min_block]
            if all(w == "" for w in window):
                continue
            h = hashlib.md5("\n".join(window).encode()).hexdigest()
            windows[h].add((path, i))

    # Lines covered by any window that appears in 2+ files.
    dup = defaultdict(set)
    for locs in windows.values():
        if len({p for p, _ in locs}) < 2:
            continue
        for p, i in locs:
            dup[p].update(range(i, i + args.min_block))

    # Merge contiguous duplicated lines into maximal ranges, group by content.
    groups = defaultdict(list)
    for path, lines in dup.items():
        normed = file_lines[path]
        for a, b in merge_ranges(lines):
            content = "\n".join(normed[a:b + 1])
            sig = hashlib.md5(content.encode()).hexdigest()
            groups[sig].append((path, a + 1, b + 1))

    results = []
    for locs in groups.values():
        files = {p for p, _, _ in locs}
        if len(files) < 2:
            continue
        span = max(b - a + 1 for _, a, b in locs)
        results.append((len(files), span, locs))
    results.sort(key=lambda x: (-x[0], -x[1]))

    print(f"=== {len(results)} duplicate block(s) across {len(file_lines)} "
          f"files (>= {args.min_block} normalized lines, >= 2 files) ===")
    for shown, (nfiles, span, locs) in enumerate(results[:args.limit], 1):
        print(f"\n[{shown}] {nfiles} files, ~{span} lines:")
        for path, a, b in sorted(locs)[:10]:
            print(f"    {os.path.relpath(path, root)}:{a}-{b}")
        if len(locs) > 10:
            print(f"    ... and {len(locs) - 10} more")
    if len(results) > args.limit:
        print(f"\n... and {len(results) - args.limit} more block(s)")
    if not results:
        print("No cross-file duplicates found at this block size.")


if __name__ == "__main__":
    main()
