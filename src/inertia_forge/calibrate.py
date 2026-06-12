"""Estimation calibration — close the loop, both backward and forward.

Backward: record an estimate and its eventual actual, then `calibrate accuracy`
reports the mean absolute percentage error (MAPE) and systematic bias (do
estimates run high or low?). Forward: `calibrate estimate <type>` turns the
recorded actuals for a task type into a baseline (mean + p80) you can estimate
the next task from. Records live in the telemetry store; stats are robust (p80
shrugs off outliers). Deterministic — same records, same numbers.
"""
from __future__ import annotations

import statistics


def record(estimated: float, actual: float, label: str | None = None,
           task_type: str = "", duration_seconds: float | None = None,
           outcome: str | None = None, complexity: float | None = None) -> None:
    from inertia_forge.telemetry import record as trecord
    detail: dict = {"estimated": float(estimated), "actual": float(actual), "type": task_type}
    if duration_seconds is not None:
        detail["duration"] = float(duration_seconds)
    if outcome is not None:
        detail["outcome"] = outcome
    if complexity is not None:
        detail["complexity"] = float(complexity)
    trecord("calibration", label or "estimate", float(actual), detail)


def _details(task_type: str | None = None) -> list[dict]:
    """Full calibration-record detail dicts, optionally filtered to a type."""
    from inertia_forge.telemetry import events
    out = []
    for ev in events(kind="calibration", limit=2000):
        d = ev.get("detail") or {}
        if d.get("estimated") and (not task_type or d.get("type", "") == task_type):
            out.append(d)
    return out


# Default effort by task-type name (overridden by complexity when present).
_EFFORT_BY_TYPE = {"test": "low", "docs": "low", "chore": "low", "style": "low",
                   "bugfix": "medium", "structural": "medium", "fix": "medium",
                   "refactor": "high", "feature": "high", "generation": "high", "rewrite": "high"}


def effort_for_type(task_type: str) -> str:
    return _EFFORT_BY_TYPE.get(task_type, "medium")


def type_stats(task_type: str = "", family: str = "anthropic") -> dict | None:
    """The full per-type calibration record (sample_count, avg/std/p80 tokens,
    avg_duration, success_rate, recommended tier/model/effort, MAPE, cx/min)."""
    from inertia_forge.models import recommend_model
    dets = _details(task_type or None)
    if not dets:
        return None
    actuals = [d["actual"] for d in dets]
    avg_tokens = round(statistics.fmean(actuals), 1)
    durs = [d["duration"] for d in dets if "duration" in d]
    avg_dur = round(statistics.fmean(durs), 1) if durs else 0.0
    outcomes = [d["outcome"] for d in dets if "outcome" in d]
    success_rate = (round(100 * sum(o == "success" for o in outcomes) / len(outcomes), 1)
                    if outcomes else None)
    cxs = [float(d["complexity"]) for d in dets if "complexity" in d]
    cx_per_minute = (round(statistics.fmean(cxs) / (avg_dur / 60), 3) if cxs and avg_dur else None)
    _, mape, _ = accuracy(task_type or None)
    tier, model = recommend_model(avg_tokens, family)
    rec_effort = effort(statistics.fmean(cxs)) if cxs else effort_for_type(task_type)
    return {
        "task_type": task_type or "all", "sample_count": len(dets),
        "avg_tokens": avg_tokens, "std_dev": round(statistics.pstdev(actuals), 1),
        "p80_tokens": round(_percentile(sorted(actuals), 80), 1),
        "avg_duration_seconds": avg_dur, "success_rate": success_rate,
        "recommended_tier": tier, "recommended_model": model,
        "recommended_effort": rec_effort, "estimation_mape": mape,
        "cx_per_minute": cx_per_minute,
    }


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

