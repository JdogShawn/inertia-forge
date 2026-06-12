"""v0.34.0 — estimation calibration loop + query interface over telemetry.
Deterministic aggregates: MAPE/bias, success rate, outcome breakdown.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import calibrate, query, telemetry
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestCalibrate:
    def test_accuracy_detects_underestimate(self, proj: Path) -> None:
        calibrate.record(5, 8)
        calibrate.record(10, 12)
        n, mape, bias = calibrate.accuracy()
        assert n == 2 and mape is not None and bias > 1  # actuals exceed estimates

    def test_perfect_estimate(self, proj: Path) -> None:
        calibrate.record(5, 5)
        n, mape, bias = calibrate.accuracy()
        assert mape == 0.0 and bias == 1.0

    def test_no_data(self, proj: Path) -> None:
        assert calibrate.accuracy() == (0, None, None)

    def test_cli(self, proj: Path, capsys) -> None:
        assert main(["calibrate", "record", "--estimated", "5", "--actual", "7"]) == 0
        assert main(["calibrate", "accuracy"]) == 0
        assert "sample" in capsys.readouterr().out


class TestQuery:
    def test_success_rate(self, proj: Path) -> None:
        telemetry.record("outcome", "success")
        telemetry.record("outcome", "fail")
        rate, breakdown = query.success_rate()
        assert rate == 50.0 and breakdown == {"success": 1, "fail": 1}

    def test_no_outcomes(self, proj: Path) -> None:
        assert query.success_rate() == (None, {})

    def test_cli_subcommands(self, proj: Path) -> None:
        telemetry.record("outcome", "success")
        calibrate.record(5, 5)
        telemetry.record("qc", "qc_pass_rate", 100.0)
        assert main(["query", "success-rate"]) == 0
        assert main(["query", "outcomes"]) == 0
        assert main(["query", "estimation-accuracy"]) == 0
        assert main(["query", "qc"]) == 0

    def test_cli_empty_paths(self, proj: Path) -> None:
        assert main(["query", "success-rate"]) == 0  # no data → advisory
        assert main(["query", "qc"]) == 0
