"""v0.30.0 — deterministic SQLite telemetry/metric store (zero dependency).
Records quality snapshots + QC results; trends show the trajectory.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import telemetry
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestStore:
    def test_record_and_events(self, proj: Path) -> None:
        telemetry.record("k", "m", 1.0)
        telemetry.record("k", "m", 2.0)
        evs = telemetry.events(name="m")
        assert len(evs) == 2 and evs[0]["value"] == 2.0  # most recent first

    def test_trend_is_chronological(self, proj: Path) -> None:
        for v in (10, 20, 30):
            telemetry.record("snapshot", "cov", v)
        assert [v for _, v in telemetry.trend("cov")] == [10, 20, 30]

    def test_detail_roundtrip(self, proj: Path) -> None:
        telemetry.record("qc", "r", 100.0, {"passed": 3, "total": 3})
        assert telemetry.events(name="r")[0]["detail"] == {"passed": 3, "total": 3}

    def test_filter_by_kind(self, proj: Path) -> None:
        telemetry.record("a", "x", 1)
        telemetry.record("b", "y", 2)
        assert {e["name"] for e in telemetry.events(kind="a")} == {"x"}

    def test_is_real_sqlite(self, proj: Path) -> None:
        import sqlite3
        telemetry.record("k", "m", 1.0)
        c = sqlite3.connect(str(proj / ".forge" / "telemetry.db"))
        assert c.execute("SELECT count(*) FROM events").fetchone()[0] == 1


class TestSnapshot:
    def test_metrics(self, proj: Path) -> None:
        src = proj / "src"
        src.mkdir()
        (src / "m.py").write_text(
            '"""Mod."""\n'
            "def good(x: int) -> int:\n    \"\"\"Doc.\"\"\"\n    return x\n"
            "def undoc(y):\n    return y\n", encoding="utf-8")
        m = telemetry.snapshot_metrics("src")
        assert m["docstring_pct"] == 50.0 and m["typehint_pct"] == 50.0
        assert m["arch_p0"] == 0.0


class TestCli:
    def test_snapshot_then_summary(self, proj: Path, capsys) -> None:
        (proj / "src").mkdir()
        (proj / "src" / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        assert main(["telemetry", "snapshot", "--path", "src"]) == 0
        capsys.readouterr()
        assert main(["telemetry", "summary"]) == 0
        assert "docstring_pct" in capsys.readouterr().out

    def test_record_and_trend(self, proj: Path, capsys) -> None:
        main(["telemetry", "record", "mymetric", "42"])
        assert main(["telemetry", "trend", "mymetric"]) == 0
        assert "42" in capsys.readouterr().out

    def test_qc_emits_pass_rate(self, proj: Path) -> None:
        suite = proj / "s.qc.yaml"
        suite.write_text("scenarios:\n  - name: ok\n    steps:\n      - file_exists: s.qc.yaml\n",
                         encoding="utf-8")
        assert main(["qc", str(suite)]) == 0
        evs = telemetry.events(name="qc_pass_rate")
        assert evs and evs[0]["value"] == 100.0
