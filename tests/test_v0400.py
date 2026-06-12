"""v0.40.0 — calibrate enriched: per-task-type baselines + forward estimation
(mean + p80) and per-type accuracy, alongside the backward MAPE/bias.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import calibrate
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestPercentile:
    def test_bounds_and_median(self) -> None:
        assert calibrate._percentile([1, 2, 3, 4, 5], 0) == 1
        assert calibrate._percentile([1, 2, 3, 4, 5], 100) == 5
        assert calibrate._percentile([1, 2, 3, 4, 5], 50) == 3
        assert calibrate._percentile([], 80) == 0.0


class TestBaselines:
    def test_per_type_and_all_bucket(self, proj: Path) -> None:
        calibrate.record(5, 8, task_type="gen")
        calibrate.record(3, 4, task_type="gen")
        calibrate.record(10, 20, task_type="struct")
        b = calibrate.baselines()
        assert b["gen"]["n"] == 2 and b["gen"]["mean"] == 6
        assert b["struct"]["n"] == 1
        assert b[""]["n"] == 3  # all-types bucket

    def test_forward_estimate_cli(self, proj: Path, capsys) -> None:
        calibrate.record(5, 8, task_type="gen")
        calibrate.record(3, 12, task_type="gen")
        assert main(["calibrate", "estimate", "--type", "gen"]) == 0
        out = capsys.readouterr().out
        assert "mean 10" in out and "p80" in out

    def test_estimate_no_data(self, proj: Path) -> None:
        assert main(["calibrate", "estimate", "--type", "nope"]) == 0


class TestPerTypeAccuracy:
    def test_filter_by_type(self, proj: Path) -> None:
        calibrate.record(5, 10, task_type="a")   # bias 2.0
        calibrate.record(5, 5, task_type="b")    # bias 1.0
        n, mape, bias = calibrate.accuracy("a")
        assert n == 1 and bias == 2.0
        n_all, _, _ = calibrate.accuracy()
        assert n_all == 2

    def test_cli_accuracy_typed(self, proj: Path) -> None:
        calibrate.record(5, 6, task_type="x")
        assert main(["calibrate", "accuracy", "--type", "x"]) == 0
