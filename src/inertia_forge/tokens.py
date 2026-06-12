"""Deterministic token estimator — budget projections without a tokenizer dep.

A transparent heuristic blend (the larger of chars/4 and words×1.3) that tracks
real tokenizers closely enough for planning, with zero dependencies. `tokens
<path>` estimates a file or a directory tree; plan estimation and budget
projection build on it.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def estimate_text(text: str) -> int:
    """Estimated token count for a string (max of chars/4 and words×1.3)."""
    return max(len(text) // 4, round(len(text.split()) * 1.3))


def estimate_file(path: str | Path) -> int:
    try:
        return estimate_text(Path(path).read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return 0


def _files(target: str, glob: str) -> list[Path]:
    p = Path(target)
    if p.is_dir():
        return sorted(f for f in p.rglob(glob) if f.is_file())
    return [p]


def run_tokens(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="inertia-forge tokens")
    parser.add_argument("paths", nargs="+", help="files or directories")
    parser.add_argument("--glob", default="*", help="file glob when a path is a dir")
    parser.add_argument("--quiet", action="store_true", help="print only the total")
    args = parser.parse_args(argv)
    from inertia_forge.palette import paint
    total = 0
    for target in args.paths:
        for f in _files(target, args.glob):
            n = estimate_file(f)
            total += n
            if not args.quiet:
                print(f"  {paint(f'{n:>8}', 'accent')}  {f}")
    print(f"{paint(f'~{total}', 'accent', bold=True)} tokens estimated")
    return 0
