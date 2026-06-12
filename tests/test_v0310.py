"""v0.31.0 — telemetry signals (regression detection) + session outcomes.
Completes the telemetry points: outcomes + threshold signals. Deterministic.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import signals, telemetry
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestSignals:
    def test_higher_better_drop_flagged(self, proj: Path) -> None:
        telemetry.record("snapshot", "coverage_pct", 90)
        telemetry.record("snapshot", "coverage_pct", 80)
        assert ("coverage_pct", 90.0, 80.0, "dropped") in signals.regressions()

    def test_lower_better_rise_flagged(self, proj: Path) -> None:
        telemetry.record("snapshot", "arch_p0", 0)
        telemetry.record("snapshot", "arch_p0", 3)
        assert any(r[0] == "arch_p0" and r[3] == "rose" for r in signals.regressions())

    def test_improvement_not_flagged(self, proj: Path) -> None:
        telemetry.record("snapshot", "docstring_pct", 50)
        telemetry.record("snapshot", "docstring_pct", 80)
        assert signals.regressions() == []

    def test_single_snapshot_no_signal(self, proj: Path) -> None:
        telemetry.record("snapshot", "typehint_pct", 50)
        assert signals.regressions() == []

    def test_check_exits_1_and_records_signal(self, proj: Path) -> None:
        telemetry.record("snapshot", "typehint_pct", 100)
        telemetry.record("snapshot", "typehint_pct", 70)
        assert main(["telemetry", "check"]) == 1
        sig = telemetry.events(kind="signal")
        assert sig and sig[0]["name"] == "regression:typehint_pct"

    def test_check_clean_exits_0(self, proj: Path) -> None:
        telemetry.record("snapshot", "coverage_pct", 80)
        telemetry.record("snapshot", "coverage_pct", 85)
        assert main(["telemetry", "check"]) == 0


class TestOutcome:
    def test_records_with_detail(self, proj: Path) -> None:
        assert main(["telemetry", "outcome", "fail", "--detail", "timeout"]) == 0
        ev = telemetry.events(kind="outcome")[0]
        assert ev["name"] == "fail" and ev["detail"] == {"detail": "timeout"}

    def test_records_success(self, proj: Path) -> None:
        assert main(["telemetry", "outcome", "success"]) == 0
        assert telemetry.events(kind="outcome")[0]["name"] == "success"
