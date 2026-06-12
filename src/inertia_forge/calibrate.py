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
           task_type: str = "", duration_seconds: float | None = None) -> None:
    from inertia_forge.telemetry import record as trecord
    detail: dict = {"estimated": float(estimated), "actual": float(actual), "type": task_type}
    if duration_seconds is not None:
        detail["duration"] = float(duration_seconds)
    trecord("calibration", label or "estimate", float(actual), detail)


def durations(task_type: str | None = None) -> list[float]:
    from inertia_forge.telemetry import events
    out = []
    for ev in events(kind="calibration", limit=2000):
        d = ev.get("detail") or {}
        if "duration" in d and task_type in (None, "", d.get("type", "")):
            out.append(float(d["duration"]))
    return out


def estimate_duration(task_type: str | None = None) -> dict[str, float] | None:
    """{n, avg_minutes, p80_minutes} from recorded durations (seconds), or None."""
    durs = durations(task_type)
    if not durs:
        return None
    avg = statistics.fmean(durs)
    p80 = _percentile(sorted(durs), 80)
    return {"n": len(durs), "avg_minutes": round(avg / 60, 1), "p80_minutes": round(p80 / 60, 1)}


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
    """{type: {n, mean, std, p80}} over recorded actuals; '' = all-types bucket."""
    from collections import defaultdict
    buckets: dict[str, list[float]] = defaultdict(list)
    for _, actual, task_type in _records():
        buckets[task_type].append(actual)
        buckets[""].append(actual)
    out = {}
    for task_type, vals in buckets.items():
        sv = sorted(vals)
        out[task_type] = {"n": len(sv), "mean": round(statistics.fmean(sv), 2),
                          "std": round(statistics.pstdev(sv), 2),  # population std
                          "p80": round(_percentile(sv, 80), 2)}
    return out


def effort(complexity: float) -> str:
    """Map a complexity score to an effort level (low <20, medium <=40, else high)."""
    if complexity < 20:
        return "low"
    if complexity <= 40:
        return "medium"
    return "high"


def budget_fit(estimated: float, budget: float, target: float = 0.8) -> dict[str, float | bool]:
    """Does an estimate fit a budget at *target* utilization? {fits, utilization}."""
    util = estimated / budget if budget else 0.0
    return {"fits": util <= target, "utilization": round(util, 3)}


def run_calibrate(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge calibrate")
    sub = p.add_subparsers(dest="sub", required=True)
    r = sub.add_parser("record", help="log an estimate vs its actual")
    r.add_argument("--estimated", type=float, required=True)
    r.add_argument("--actual", type=float, required=True)
    r.add_argument("--type", default="", help="task type (e.g. structural/generation/test)")
    r.add_argument("--duration", type=float, default=None, help="actual duration in seconds")
    r.add_argument("--label")
    a = sub.add_parser("accuracy", help="MAPE + bias across records")
    a.add_argument("--type", default=None)
    e = sub.add_parser("estimate", help="forward token baseline (mean + std + p80)")
    e.add_argument("--type", default="")
    du = sub.add_parser("duration", help="forward duration estimate (avg + p80 minutes)")
    du.add_argument("--type", default="")
    md = sub.add_parser("model", help="recommend a model tier for a type")
    md.add_argument("--type", default=""); md.add_argument("--family", default="anthropic")
    ef = sub.add_parser("effort", help="effort level for a complexity score")
    ef.add_argument("complexity", type=float)
    bg = sub.add_parser("budget", help="does an estimate fit a budget?")
    bg.add_argument("--estimated", type=float, required=True)
    bg.add_argument("--budget", type=float, required=True)
    bg.add_argument("--target", type=float, default=0.8)
    return _dispatch(p.parse_args(argv))


def _dispatch(args: argparse.Namespace) -> int:
    from inertia_forge.glyphs import g, seal
    if args.sub == "record":
        record(args.estimated, args.actual, args.label, args.type, args.duration)
        print(f"{seal('ok')} recorded estimate {args.estimated:g} vs actual {args.actual:g}")
        return 0
    if args.sub == "estimate":
        base = baselines().get(args.type or "")
        if not base:
            print(f"(no calibration data for type {args.type or 'all'!r})")
            return 0
        print(f"{seal('ok')} {args.type or 'all'}: n={base['n']:g} {g('dot')} mean {base['mean']:g} "
              f"{g('dot')} std {base['std']:g} {g('dot')} p80 {base['p80']:g}")
        return 0
    if args.sub == "duration":
        est = estimate_duration(args.type or None)
        if not est:
            print(f"(no duration data for type {args.type or 'all'!r})")
            return 0
        print(f"{seal('ok')} {args.type or 'all'}: n={est['n']:g} {g('dot')} avg {est['avg_minutes']:g}min "
              f"{g('dot')} p80 {est['p80_minutes']:g}min")
        return 0
    if args.sub == "model":
        from inertia_forge.models import recommend_model
        avg = (baselines().get(args.type or "") or {}).get("mean", 0.0)
        tier, model = recommend_model(avg, args.family)
        print(f"{seal('ok')} {args.type or 'all'} (avg {avg:g} tokens) {g('arrow_r')} "
              f"{args.family} {g('dot')} {tier} {g('dot')} {model}")
        return 0
    if args.sub == "effort":
        print(f"{seal('ok')} complexity {args.complexity:g} {g('arrow_r')} {effort(args.complexity)}")
        return 0
    if args.sub == "budget":
        fit = budget_fit(args.estimated, args.budget, args.target)
        verdict = "fits" if fit["fits"] else "OVER budget"
        print(f"{seal('ok' if fit['fits'] else 'error')} {args.estimated:g}/{args.budget:g} "
              f"= {fit['utilization']:g} util (target {args.target:g}) {g('dot')} {verdict}")
        return 0 if fit["fits"] else 1
    n, mape, bias = accuracy(args.type)
    if not n:
        print("(no calibration data — `calibrate record --estimated N --actual M`)")
        return 0
    tend = "over-estimates" if bias < 1 else ("under-estimates" if bias > 1 else "spot-on")
    print(f"{seal('ok')} {n} sample(s) {g('dot')} MAPE {mape:g}% {g('dot')} bias {bias:g}x ({tend})")
    return 0
