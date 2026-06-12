"""Estimation calibration — close the loop, both backward and forward.

Backward: record an estimate and its eventual actual, then `calibrate accuracy`
reports the mean absolute percentage error (MAPE) and systematic bias (do
estimates run high or low?). Forward: `calibrate estimate <type>` turns the
recorded actuals for a task type into a baseline (mean + p80) you can estimate
the next task from. Records live in the telemetry store; stats are robust (p80
shrugs off outliers). Deterministic — same records, same numbers.
"""
from __future__ import annotations

import argparse
import statistics


def record(estimated: float, actual: float, label: str | None = None,
           task_type: str = "") -> None:
    from inertia_forge.telemetry import record as trecord
    trecord("calibration", label or "estimate", float(actual),
            {"estimated": float(estimated), "actual": float(actual), "type": task_type})


def _records() -> list[tuple[float, float, str]]:
    from inertia_forge.telemetry import events
    out = []
    for ev in events(kind="calibration", limit=2000):
        d = ev.get("detail") or {}
        if d.get("estimated"):
            out.append((float(d["estimated"]), float(d["actual"]), d.get("type", "")))
    return out


def accuracy(task_type: str | None = None) -> tuple[int, float | None, float | None]:
    """(samples, MAPE %, bias). bias<1 over-estimates; >1 under-estimates."""
    pairs = [(e, a) for e, a, t in _records() if task_type in (None, "", t) or t == task_type]
    if not pairs:
        return 0, None, None
    mape = 100 * statistics.fmean(abs(a - e) / e for e, a in pairs)
    bias = statistics.fmean(a / e for e, a in pairs)
    return len(pairs), round(mape, 1), round(bias, 3)


def _percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * pct / 100
    lo = int(k)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def baselines() -> dict[str, dict[str, float]]:
    """{type: {n, mean, p80}} over recorded actuals; '' is the all-types bucket."""
    from collections import defaultdict
    buckets: dict[str, list[float]] = defaultdict(list)
    for _, actual, task_type in _records():
        buckets[task_type].append(actual)
        buckets[""].append(actual)
    out = {}
    for task_type, vals in buckets.items():
        sv = sorted(vals)
        out[task_type] = {"n": len(sv), "mean": round(statistics.fmean(sv), 2),
                          "p80": round(_percentile(sv, 80), 2)}
    return out


def run_calibrate(argv: list[str]) -> int:
    from inertia_forge.glyphs import g, seal
    p = argparse.ArgumentParser(prog="inertia-forge calibrate")
    sub = p.add_subparsers(dest="sub", required=True)
    r = sub.add_parser("record", help="log an estimate vs its actual")
    r.add_argument("--estimated", type=float, required=True)
    r.add_argument("--actual", type=float, required=True)
    r.add_argument("--type", default="", help="task type (e.g. structural/generation/test)")
    r.add_argument("--label")
    a = sub.add_parser("accuracy", help="MAPE + bias across records")
    a.add_argument("--type", default=None)
    e = sub.add_parser("estimate", help="forward baseline (mean + p80) for a type")
    e.add_argument("--type", default="")
    args = p.parse_args(argv)

    if args.sub == "record":
        record(args.estimated, args.actual, args.label, args.type)
        print(f"{seal('ok')} recorded estimate {args.estimated:g} vs actual {args.actual:g}")
        return 0
    if args.sub == "estimate":
        base = baselines().get(args.type or "")
        if not base:
            print(f"(no calibration data for type {args.type or 'all'!r})")
            return 0
        print(f"{seal('ok')} {args.type or 'all'}: n={base['n']:g} {g('dot')} "
              f"mean {base['mean']:g} {g('dot')} p80 {base['p80']:g}")
        return 0
    n, mape, bias = accuracy(args.type)
    if not n:
        print("(no calibration data — `calibrate record --estimated N --actual M`)")
        return 0
    tend = "over-estimates" if bias < 1 else ("under-estimates" if bias > 1 else "spot-on")
    print(f"{seal('ok')} {n} sample(s) {g('dot')} MAPE {mape:g}% {g('dot')} bias {bias:g}x ({tend})")
    return 0
