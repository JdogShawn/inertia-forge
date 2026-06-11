"""Work-time tracking — start/stop/status/report. Deterministic, zero LLM.

One active timer at a time (`.forge/timer_active.json`); completed intervals
append to `.forge/timers.jsonl`. `report` aggregates total time per label.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

TIMERS = Path(".forge") / "timers.jsonl"
ACTIVE = Path(".forge") / "timer_active.json"


def start(label: str) -> bool:
    if ACTIVE.exists():
        return False
    ACTIVE.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE.write_text(json.dumps({"label": label, "start": time.time()}), encoding="utf-8")
    return True


def stop() -> dict | None:
    if not ACTIVE.exists():
        return None
    a = json.loads(ACTIVE.read_text(encoding="utf-8"))
    rec = {"label": a["label"], "start": a["start"], "duration": time.time() - a["start"]}
    with open(TIMERS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    ACTIVE.unlink()
    return rec


def active() -> dict | None:
    if not ACTIVE.exists():
        return None
    a = json.loads(ACTIVE.read_text(encoding="utf-8"))
    a["elapsed"] = time.time() - a["start"]
    return a


def totals() -> dict[str, float]:
    out: dict[str, float] = {}
    if not TIMERS.exists():
        return out
    for line in TIMERS.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        out[r["label"]] = out.get(r["label"], 0.0) + float(r.get("duration", 0))
    return out


def _fmt(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m{s:02d}s" if h else f"{m}m{s:02d}s"


def run_timer(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge timer")
    sub = p.add_subparsers(dest="sub", required=True)
    st = sub.add_parser("start"); st.add_argument("label", nargs="?", default="work")
    sub.add_parser("stop")
    sub.add_parser("status")
    sub.add_parser("report")
    args = p.parse_args(argv)
    if args.sub == "start":
        ok = start(args.label)
        print(f"started '{args.label}'" if ok else "a timer is already running — stop it first")
        return 0 if ok else 1
    if args.sub == "stop":
        rec = stop()
        print(f"stopped '{rec['label']}' after {_fmt(rec['duration'])}" if rec else "no active timer")
        return 0 if rec else 1
    if args.sub == "status":
        a = active()
        print(f"running '{a['label']}' — {_fmt(a['elapsed'])}" if a else "no active timer")
        return 0
    tot = totals()
    if not tot:
        print("(no recorded time)")
        return 0
    for label, secs in sorted(tot.items(), key=lambda kv: -kv[1]):
        print(f"  {label:24} {_fmt(secs)}")
    return 0
