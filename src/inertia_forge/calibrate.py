"""Estimation calibration — close the loop between an estimate and the actual.

Record an estimate and its eventual actual (complexity points, tokens, minutes —
whatever you estimate), then `calibrate accuracy` reports how close the forge's
estimates run: the mean absolute percentage error (MAPE) and the systematic bias
(do estimates run high or low?). Records live in the telemetry store.
Deterministic — the same records always give the same numbers.
"""
from __future__ import annotations

import argparse
import statistics


def record(estimated: float, actual: float, label: str | None = None) -> None:
    from inertia_forge.telemetry import record as trecord
    trecord("calibration", label or "estimate", float(actual),
            {"estimated": float(estimated), "actual": float(actual)})


def _pairs() -> list[tuple[float, float]]:
    from inertia_forge.telemetry import events
    out = []
    for ev in events(kind="calibration", limit=1000):
        d = ev.get("detail") or {}
        if d.get("estimated"):  # non-zero estimate
            out.append((float(d["estimated"]), float(d["actual"])))
    return out


def accuracy() -> tuple[int, float | None, float | None]:
    """(samples, MAPE %, bias ratio). bias<1 → over-estimates; >1 → under-estimates."""
    pairs = _pairs()
    if not pairs:
        return 0, None, None
    mape = 100 * statistics.fmean(abs(a - e) / e for e, a in pairs)
    bias = statistics.fmean(a / e for e, a in pairs)
    return len(pairs), round(mape, 1), round(bias, 3)


def run_calibrate(argv: list[str]) -> int:
    from inertia_forge.glyphs import g, seal
    p = argparse.ArgumentParser(prog="inertia-forge calibrate")
    sub = p.add_subparsers(dest="sub", required=True)
    r = sub.add_parser("record", help="log an estimate vs its actual")
    r.add_argument("--estimated", type=float, required=True)
    r.add_argument("--actual", type=float, required=True)
    r.add_argument("--label")
    sub.add_parser("accuracy", help="MAPE + bias across all records")
    args = p.parse_args(argv)
    if args.sub == "record":
        record(args.estimated, args.actual, args.label)
        print(f"{seal('ok')} recorded estimate {args.estimated:g} vs actual {args.actual:g}")
        return 0
    n, mape, bias = accuracy()
    if not n:
        print("(no calibration data — `calibrate record --estimated N --actual M`)")
        return 0
    tend = "over-estimates" if bias < 1 else ("under-estimates" if bias > 1 else "spot-on")
    dot = g("dot")
    print(f"{seal('ok')} {n} sample(s) {dot} MAPE {mape:g}% {dot} bias {bias:g}x ({tend})")
    return 0
