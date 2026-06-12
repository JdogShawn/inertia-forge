"""Telemetry signals — turn metric movement into a pass/fail signal.

Compares the two most recent quality snapshots and flags regressions: a
higher-is-better metric (coverage, docstring %, type-hint %) that dropped, or a
lower-is-better metric (arch P0s, dead symbols, over-complexity) that rose.
`telemetry check` records a ``signal`` event per regression and exits 1 if any —
a deterministic regression gate, with no model and no upload.
"""
from __future__ import annotations

HIGHER_BETTER = ("coverage_pct", "docstring_pct", "typehint_pct")
LOWER_BETTER = ("arch_p0", "dead_symbols", "complexity_over_10")


def _last_two(name: str) -> list[tuple[str, float]]:
    from inertia_forge.telemetry import trend
    series = trend(name, limit=2)
    return series if len(series) >= 2 else []


def regressions() -> list[tuple[str, float, float, str]]:
    """[(metric, prev, now, direction)] for each metric that moved the wrong way."""
    out: list[tuple[str, float, float, str]] = []
    for name in HIGHER_BETTER:
        if (pair := _last_two(name)) and pair[1][1] < pair[0][1]:
            out.append((name, pair[0][1], pair[1][1], "dropped"))
    for name in LOWER_BETTER:
        if (pair := _last_two(name)) and pair[1][1] > pair[0][1]:
            out.append((name, pair[0][1], pair[1][1], "rose"))
    return out


def run_check(_argv: list[str]) -> int:
    from inertia_forge.glyphs import g, seal
    from inertia_forge.telemetry import record
    regs = regressions()
    for name, prev, now, direction in regs:
        record("signal", f"regression:{name}", now, {"prev": prev, "now": now, "direction": direction})
        print(f"{seal('error')} {name} {direction}: {prev:g} {g('arrow_r')} {now:g}")
    if not regs:
        print(f"{seal('ok')} no quality regressions vs the previous snapshot")
        return 0
    return 1
