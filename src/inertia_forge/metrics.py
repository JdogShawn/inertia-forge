"""Deterministic token & cost tracking — pure counting, zero LLM.

Records usage events to `.forge/metrics.jsonl` and reports totals. Cost is
estimated ONLY from rates you configure (`.forge/rates.json`, $/1M tokens) —
no prices are fabricated; with no rates set, only token totals are shown.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

METRICS = Path(".forge") / "metrics.jsonl"
RATES = Path(".forge") / "rates.json"


def add(in_tokens: int, out_tokens: int, model: str = "default") -> None:
    METRICS.parent.mkdir(parents=True, exist_ok=True)
    with open(METRICS, "a", encoding="utf-8") as f:
        f.write(json.dumps({"in": int(in_tokens), "out": int(out_tokens), "model": model}) + "\n")


def _events() -> list[dict]:
    if not METRICS.exists():
        return []
    out: list[dict] = []
    for line in METRICS.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _rates() -> dict:
    if RATES.exists():
        try:
            return json.loads(RATES.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def totals() -> dict:
    """Per-model {in, out} token totals."""
    by_model: dict[str, dict] = {}
    for e in _events():
        d = by_model.setdefault(e.get("model", "default"), {"in": 0, "out": 0})
        d["in"] += int(e.get("in", 0))
        d["out"] += int(e.get("out", 0))
    return by_model


def _h_add(a: argparse.Namespace) -> int:
    add(a.in_tokens, a.out_tokens, a.model)
    print(f"recorded {a.in_tokens} in / {a.out_tokens} out ({a.model})")
    return 0


def _h_set_rate(a: argparse.Namespace) -> int:
    RATES.parent.mkdir(parents=True, exist_ok=True)
    rates = _rates()
    rates[a.model] = {"in": a.in_rate, "out": a.out_rate}
    RATES.write_text(json.dumps(rates, indent=2) + "\n", encoding="utf-8")
    print(f"rate set for {a.model}: ${a.in_rate}/1M in, ${a.out_rate}/1M out")
    return 0


def _h_report(_a: argparse.Namespace) -> int:
    by_model, rates = totals(), _rates()
    if not by_model:
        print("(no metrics recorded)")
        return 0
    grand = 0.0
    for model, d in sorted(by_model.items()):
        line = f"  {model:16} in={d['in']} out={d['out']}"
        r = rates.get(model)
        if r:
            cost = d["in"] / 1e6 * r["in"] + d["out"] / 1e6 * r["out"]
            grand += cost
            line += f"  ~${cost:.4f}"
        print(line)
    if grand:
        print(f"  {'TOTAL':16} ~${grand:.4f} (rates from .forge/rates.json)")
    return 0


def run_metrics(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge metrics")
    sub = p.add_subparsers(dest="sub", required=True)
    a = sub.add_parser("add", help="record a usage event")
    a.add_argument("--in", dest="in_tokens", type=int, required=True)
    a.add_argument("--out", dest="out_tokens", type=int, required=True)
    a.add_argument("--model", default="default")
    a.set_defaults(fn=_h_add)
    sr = sub.add_parser("set-rate", help="set $/1M token rates for a model")
    sr.add_argument("model")
    sr.add_argument("--in", dest="in_rate", type=float, required=True)
    sr.add_argument("--out", dest="out_rate", type=float, required=True)
    sr.set_defaults(fn=_h_set_rate)
    sub.add_parser("report", help="show token totals + estimated cost").set_defaults(fn=_h_report)
    args = p.parse_args(argv)
    return args.fn(args)
