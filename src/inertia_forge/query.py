"""Query — aggregate views over the telemetry store, for agents and humans.

  query success-rate         % of recorded outcomes that succeeded
  query outcomes             breakdown by outcome (success / fail / partial)
  query estimation-accuracy  MAPE + bias from calibration records
  query qc                   latest QC pass rate + how many runs

Deterministic reads of .forge/telemetry.db. Pairs with `json` for machine output.
"""
from __future__ import annotations

import argparse
from collections import Counter


def success_rate() -> tuple[float | None, dict[str, int]]:
    from inertia_forge.telemetry import events
    outs = [e["name"] for e in events(kind="outcome", limit=2000)]
    if not outs:
        return None, {}
    counts = Counter(outs)
    return round(100 * counts.get("success", 0) / len(outs), 1), dict(counts)


def run_query(argv: list[str]) -> int:
    from inertia_forge.glyphs import g, seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge query")
    sub = p.add_subparsers(dest="sub", required=True)
    for name, help_ in (("success-rate", "outcome success rate"),
                        ("outcomes", "outcome breakdown"),
                        ("estimation-accuracy", "calibration MAPE + bias"),
                        ("qc", "latest QC pass rate")):
        sub.add_parser(name, help=help_)
    args = p.parse_args(argv)

    if args.sub in ("success-rate", "outcomes"):
        rate, breakdown = success_rate()
        if rate is None:
            print("(no outcomes recorded — `telemetry outcome success|fail|partial`)")
            return 0
        if args.sub == "success-rate":
            print(f"{seal('ok')} success rate {paint(f'{rate:g}%', 'success', bold=True)} "
                  f"({breakdown.get('success', 0)}/{sum(breakdown.values())})")
        else:
            for k in sorted(breakdown):
                print(f"  {paint(k.ljust(10), 'muted')} {breakdown[k]}")
        return 0
    if args.sub == "estimation-accuracy":
        from inertia_forge.calibrate import accuracy
        n, mape, bias = accuracy()
        if not n:
            print("(no calibration data — `calibrate record ...`)")
            return 0
        print(f"{seal('ok')} {n} sample(s) {g('dot')} MAPE {mape:g}% {g('dot')} bias {bias:g}x")
        return 0
    from inertia_forge.telemetry import trend
    series = trend("qc_pass_rate")
    if not series:
        print("(no QC runs recorded)")
        return 0
    print(f"{seal('ok')} latest QC pass rate {paint(f'{series[-1][1]:g}%', 'success', bold=True)} "
          f"over {len(series)} run(s)")
    return 0
