"""Telemetry — a deterministic, local SQLite metric store for quality over time.

Records timestamped events and metric values to ``.forge/telemetry.db`` (stdlib
sqlite3 — zero dependency, fully offline). The QC runner and `telemetry snapshot`
emit here; a snapshot captures the project's current quality numbers (arch P0s,
dead symbols, docstring/type-hint %, over-complexity count, coverage) in one
pass, and `telemetry trend <metric>` shows a metric's trajectory so a regression
reads as a slope, not a guess. No model, no upload — telemetry never leaves the
machine.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB = Path(".forge") / "telemetry.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL, kind TEXT NOT NULL, name TEXT NOT NULL,
  value REAL, detail TEXT
);
CREATE INDEX IF NOT EXISTS idx_events_name ON events(name);
CREATE INDEX IF NOT EXISTS idx_events_kind ON events(kind);
"""


def _conn() -> sqlite3.Connection:
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB))
    c.executescript(_SCHEMA)
    return c


def record(kind: str, name: str, value: float | None = None,
           detail: dict | None = None, ts: str | None = None) -> str:
    """Append one telemetry event. Returns its timestamp. Never raises upward."""
    stamp = ts or datetime.now(timezone.utc).isoformat()
    try:
        with _conn() as c:
            c.execute("INSERT INTO events (ts, kind, name, value, detail) VALUES (?,?,?,?,?)",
                      (stamp, kind, name, None if value is None else float(value),
                       json.dumps(detail) if detail is not None else None))
    except sqlite3.Error:
        pass
    return stamp


def events(kind: str | None = None, name: str | None = None, limit: int = 100) -> list[dict]:
    q, where, args = "SELECT ts, kind, name, value, detail FROM events", [], []
    if kind:
        where.append("kind=?"); args.append(kind)
    if name:
        where.append("name=?"); args.append(name)
    if where:
        q += " WHERE " + " AND ".join(where)
    q += " ORDER BY id DESC LIMIT ?"; args.append(limit)
    with _conn() as c:
        return [{"ts": r[0], "kind": r[1], "name": r[2], "value": r[3],
                 "detail": json.loads(r[4]) if r[4] else None} for r in c.execute(q, args)]


def trend(name: str, limit: int = 20) -> list[tuple[str, float]]:
    """[(ts, value)] oldest→newest for a metric name."""
    with _conn() as c:
        rows = c.execute("SELECT ts, value FROM events WHERE name=? AND value IS NOT NULL "
                         "ORDER BY id DESC LIMIT ?", (name, limit)).fetchall()
    return list(reversed(rows))


def snapshot_metrics(path: str) -> dict[str, float]:
    """Compute the project's current quality numbers in one pass. Deterministic."""
    from inertia_forge import complexity as cx, deadcode, docstrings, typehints
    from inertia_forge.independent_analyzer import analyze_directory
    src = Path(path)
    out: dict[str, float] = {}
    findings = analyze_directory(src) if src.exists() else []
    out["arch_p0"] = float(sum(1 for f in findings if f.get("severity") == "P0"))
    out["dead_symbols"] = float(len(deadcode.find_dead(src))) if src.exists() else 0.0
    docd = [ok for f in docstrings._collect(path) for _, ok in docstrings.analyze_file(f)]
    out["docstring_pct"] = round(100 * sum(docd) / len(docd), 1) if docd else 100.0
    typ = [ok for f in docstrings._collect(path) for _, ok in typehints.analyze_file(f)]
    out["typehint_pct"] = round(100 * sum(typ) / len(typ), 1) if typ else 100.0
    out["complexity_over_10"] = float(sum(
        1 for f in cx._collect(path) for _, c, _ in cx.analyze_file(f) if c > 10))
    cov = Path("coverage.xml")
    if cov.exists():
        from inertia_forge.coverage import parse_coverage
        total, _ = parse_coverage(cov)
        if total is not None:
            out["coverage_pct"] = round(total, 1)
    return out


def _cmd_snapshot(args: argparse.Namespace) -> int:
    from inertia_forge.glyphs import seal
    metrics = snapshot_metrics(args.path)
    for name, value in metrics.items():
        record("snapshot", name, value)
    print(f"{seal('ok')} recorded {len(metrics)} metric(s): "
          + ", ".join(f"{k}={v:g}" for k, v in metrics.items()))
    return 0


def _cmd_trend(args: argparse.Namespace) -> int:
    from inertia_forge.glyphs import g
    from inertia_forge.palette import paint
    series = trend(args.name)
    if not series:
        print(f"(no data for {args.name})")
        return 0
    for ts, val in series:
        bar = paint(g("orbit") * min(int(val / 5) + 1, 20), "accent")
        print(f"  {ts[:19]}  {paint(f'{val:7g}', 'text')}  {bar}")
    return 0


def _cmd_summary(_args: argparse.Namespace) -> int:
    from inertia_forge.palette import paint
    snaps: dict[str, float] = {}
    for ev in events(kind="snapshot", limit=200):
        snaps.setdefault(ev["name"], ev["value"])  # most recent first
    if not snaps:
        print("(no snapshots yet — run `telemetry snapshot`)")
        return 0
    for name in sorted(snaps):
        print(f"  {paint(name.ljust(20), 'muted')} {snaps[name]:g}")
    return 0


def run_telemetry(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge telemetry")
    sub = p.add_subparsers(dest="sub", required=True)
    snap = sub.add_parser("snapshot", help="record current quality metrics")
    snap.add_argument("--path", default="src")
    tr = sub.add_parser("trend", help="show a metric's trajectory"); tr.add_argument("name")
    rec = sub.add_parser("record", help="record a custom metric")
    rec.add_argument("name"); rec.add_argument("value", type=float); rec.add_argument("--kind", default="custom")
    sub.add_parser("summary", help="latest snapshot values")
    sub.add_parser("check", help="flag quality regressions vs the previous snapshot")
    oc = sub.add_parser("outcome", help="record a session/task outcome")
    oc.add_argument("result", choices=("success", "fail", "partial"))
    oc.add_argument("--detail", help="user_stop / compaction / rate_limit / code_failure / timeout")
    args = p.parse_args(argv)
    if args.sub == "snapshot":
        return _cmd_snapshot(args)
    if args.sub == "trend":
        return _cmd_trend(args)
    if args.sub == "summary":
        return _cmd_summary(args)
    if args.sub == "check":
        from inertia_forge.signals import run_check
        return run_check([])
    if args.sub == "outcome":
        record("outcome", args.result, detail={"detail": args.detail} if args.detail else None)
        print(f"{seal('ok')} recorded outcome: {args.result}"
              + (f" ({args.detail})" if args.detail else ""))
        return 0
    record(args.kind, args.name, args.value)
    print(f"{seal('ok')} recorded {args.name}={args.value:g}")
    return 0
