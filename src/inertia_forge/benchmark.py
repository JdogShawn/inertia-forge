"""Deterministic micro-benchmark of the forge's own operations (timing only).

Measures how long the core deterministic operations take on a target tree —
registry load, code analysis, unused-import sweep. Useful to catch a
performance regression in the forge itself. (Timing is measurement, not
enforcement logic — the gates stay deterministic.)
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path


def _median_ms(fn, runs: int) -> float:
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        fn()
        times.append((time.perf_counter() - start) * 1000.0)
    times.sort()
    return times[len(times) // 2]


def run_benchmark(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="inertia-forge benchmark")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args(argv)

    import inertia_forge.skill_registry as sr
    from inertia_forge.independent_analyzer import analyze_directory
    from inertia_forge.sweep import sweep_path

    p = Path(args.path)

    def _load_registry() -> None:
        sr._cache = None
        sr.get_all_skills()

    ops = [
        ("registry_load", _load_registry),
        ("analyze_dir", lambda: analyze_directory(p)),
        ("sweep", lambda: sweep_path(p)),
    ]
    for name, fn in ops:
        print(f"  {name:16} {_median_ms(fn, args.runs):7.1f} ms  (median of {args.runs})")
    return 0
