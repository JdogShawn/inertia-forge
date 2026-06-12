"""Test-coverage gate — parse a Cobertura coverage.xml and enforce a floor.

`verify` runs the tests; this reads the coverage report they produce (e.g.
``pytest --cov --cov-report=xml``) and gates on a total line-coverage threshold,
optionally per file, listing the files that fall short. Deterministic XML
parsing — no coverage tool needed at read time. Missing report → advisory, not
a failure (you may not have generated one).
"""
from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_coverage(path: str | Path) -> tuple[float | None, list[tuple[str, float]]]:
    """(total_pct, [(filename, pct)]) from a Cobertura coverage.xml, or (None, [])."""
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError):
        return None, []
    total = float(root.get("line-rate", 0.0)) * 100
    files = [(cls.get("filename", "?"), float(cls.get("line-rate", 0.0)) * 100)
             for cls in root.iter("class")]
    return total, sorted(files)


def run_coverage(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge coverage")
    p.add_argument("file", nargs="?", default="coverage.xml", help="Cobertura XML")
    p.add_argument("--min", type=float, default=80.0, help="minimum total coverage %%")
    p.add_argument("--per-file", type=float, help="also require each file at this %%")
    args = p.parse_args(argv)

    if not Path(args.file).exists():
        print(f"{seal('warn')} no coverage report at {args.file} "
              f"(run: pytest --cov --cov-report=xml)")
        return 0
    total, files = parse_coverage(args.file)
    if total is None:
        print(f"{seal('error')} could not parse {args.file}")
        return 1
    low = [(f, r) for f, r in files if args.per_file is not None and r < args.per_file]
    for f, r in low:
        print(f"  {paint(f'{r:5.1f}%', 'warn')}  {f}")
    ok = total >= args.min and not low
    suffix = f", per-file {args.per_file:g}%" if args.per_file is not None else ""
    pct = paint(f"{total:.1f}%", "success" if total >= args.min else "error", bold=True)
    print(f"\n{seal('ok' if ok else 'error')} total coverage {pct} (min {args.min:g}%{suffix})")
    return 0 if ok else 1
