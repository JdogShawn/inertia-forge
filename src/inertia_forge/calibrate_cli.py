"""CLI for `inertia-forge calibrate` — kept out of calibrate.py so the logic
module stays pure and under the architecture limits.
"""
from __future__ import annotations

import argparse

from inertia_forge import calibrate as c


def _show_stats(args: argparse.Namespace) -> int:
    from inertia_forge.glyphs import seal
    from inertia_forge.palette import paint
    s = c.type_stats(args.type, args.family)
    if not s:
        print(f"(no calibration data for type {args.type or 'all'!r})")
        return 0
    print(f"{seal('ok')} {paint(s['task_type'], 'accent', bold=True)} "
          f"(n={s['sample_count']}, family={args.family})")
    for k in ("avg_tokens", "std_dev", "p80_tokens", "avg_duration_seconds",
              "success_rate", "estimation_mape", "cx_per_minute",
              "recommended_tier", "recommended_model", "recommended_effort"):
        v = s[k]
        print(f"  {paint(k.ljust(22), 'muted')} {v if v is not None else '-'}")
    return 0


def _dispatch(args: argparse.Namespace) -> int:
    from inertia_forge.glyphs import g, seal
    if args.sub == "record":
        c.record(args.estimated, args.actual, args.label, args.type, args.duration,
                 args.outcome, args.complexity)
        print(f"{seal('ok')} recorded estimate {args.estimated:g} vs actual {args.actual:g}")
        return 0
    if args.sub == "stats":
        return _show_stats(args)
    if args.sub == "estimate":
        base = c.baselines().get(args.type or "")
        if not base:
            print(f"(no calibration data for type {args.type or 'all'!r})")
            return 0
        print(f"{seal('ok')} {args.type or 'all'}: n={base['n']:g} {g('dot')} mean {base['mean']:g} "
              f"{g('dot')} std {base['std']:g} {g('dot')} p80 {base['p80']:g}")
        return 0
    if args.sub == "duration":
        est = c.estimate_duration(args.type or None)
        if not est:
            print(f"(no duration data for type {args.type or 'all'!r})")
            return 0
        print(f"{seal('ok')} {args.type or 'all'}: n={est['n']:g} {g('dot')} avg {est['avg_minutes']:g}min "
              f"{g('dot')} p80 {est['p80_minutes']:g}min")
        return 0
    if args.sub == "model":
        from inertia_forge.models import recommend_model
        avg = (c.baselines().get(args.type or "") or {}).get("mean", 0.0)
        tier, model = recommend_model(avg, args.family)
        print(f"{seal('ok')} {args.type or 'all'} (avg {avg:g} tokens) {g('arrow_r')} "
              f"{args.family} {g('dot')} {tier} {g('dot')} {model}")
        return 0
    if args.sub == "effort":
        print(f"{seal('ok')} complexity {args.complexity:g} {g('arrow_r')} {c.effort(args.complexity)}")
        return 0
    if args.sub == "budget":
        fit = c.budget_fit(args.estimated, args.budget, args.target)
        verdict = "fits" if fit["fits"] else "OVER budget"
        print(f"{seal('ok' if fit['fits'] else 'error')} {args.estimated:g}/{args.budget:g} "
              f"= {fit['utilization']:g} util (target {args.target:g}) {g('dot')} {verdict}")
        return 0 if fit["fits"] else 1
    n, mape, bias = c.accuracy(args.type)
    if not n:
        print("(no calibration data — `calibrate record --estimated N --actual M`)")
        return 0
    tend = "over-estimates" if bias < 1 else ("under-estimates" if bias > 1 else "spot-on")
    print(f"{seal('ok')} {n} sample(s) {g('dot')} MAPE {mape:g}% {g('dot')} bias {bias:g}x ({tend})")
    return 0


def run_calibrate(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge calibrate")
    sub = p.add_subparsers(dest="sub", required=True)
    r = sub.add_parser("record", help="log an estimate vs its actual")
    r.add_argument("--estimated", type=float, required=True)
    r.add_argument("--actual", type=float, required=True)
    r.add_argument("--type", default="", help="task type (e.g. structural/generation/test)")
    r.add_argument("--duration", type=float, default=None, help="actual duration in seconds")
    r.add_argument("--outcome", default=None, help="success / fail / partial")
    r.add_argument("--complexity", type=float, default=None, help="task complexity score")
    r.add_argument("--label")
    a = sub.add_parser("accuracy", help="MAPE + bias across records")
    a.add_argument("--type", default=None)
    st = sub.add_parser("stats", help="full per-type calibration record")
    st.add_argument("--type", default=""); st.add_argument("--family", default="anthropic")
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
