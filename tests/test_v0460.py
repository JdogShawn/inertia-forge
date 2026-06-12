"""v0.46.0 — calibrate gains deterministic per-type std_dev (population),
effort classification, and budget-fit.
"""
from __future__ import annotations

import statistics
from pathlib import Path

import pytest

from inertia_forge import calibrate
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestStdDev:
    def test_baseline_includes_population_std(self, proj: Path) -> None:
        for a in (8, 12, 4):
            calibrate.record(5, a, task_type="g")
        b = calibrate.baselines()["g"]
        assert b["mean"] == 8.0
        assert b["std"] == round(statistics.pstdev([8, 12, 4]), 2)  # exact population std


class TestEffort:
    def test_thresholds(self) -> None:
        assert calibrate.effort(10) == "low"      # < 20
        assert calibrate.effort(20) == "medium"   # not < 20
        assert calibrate.effort(40) == "medium"   # <= 40
        assert calibrate.effort(41) == "high"

    def test_cli(self, proj: Path, capsys) -> None:
        assert main(["calibrate", "effort", "30"]) == 0
        assert "medium" in capsys.readouterr().out


class TestBudgetFit:
    def test_fit_and_overflow(self) -> None:
        assert calibrate.budget_fit(80, 100)["fits"] is True
        assert calibrate.budget_fit(90, 100)["fits"] is False
        assert calibrate.budget_fit(80, 100)["utilization"] == 0.8

    def test_zero_budget_guard(self) -> None:
        assert calibrate.budget_fit(5, 0)["utilization"] == 0.0

    def test_cli_exit_codes(self, proj: Path) -> None:
        assert main(["calibrate", "budget", "--estimated", "50", "--budget", "100"]) == 0
        assert main(["calibrate", "budget", "--estimated", "90", "--budget", "100"]) == 1
