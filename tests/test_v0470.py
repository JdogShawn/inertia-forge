"""v0.47.0 — LLM-aware model recommender (family-agnostic tiers, 2026 registry,
.forge/models.yaml override) + full duration estimation in calibrate.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import calibrate, models
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestTiers:
    def test_token_thresholds(self) -> None:
        assert models.recommend_tier(8_000) == "small"
        assert models.recommend_tier(35_000) == "mid"
        assert models.recommend_tier(90_000) == "frontier"

    def test_complexity_bumps_up_only(self) -> None:
        assert models.recommend_tier(5_000, complexity=80) == "frontier"   # complexity wins
        assert models.recommend_tier(5_000, complexity=10) == "small"       # neither bumps
        assert models.recommend_tier(90_000, complexity=5) == "frontier"    # tokens keep it high


class TestRecommend:
    def test_family_mapping(self) -> None:
        assert models.recommend_model(90_000, "openai") == ("frontier", "gpt-5.5")
        assert models.recommend_model(35_000, "kimi") == ("mid", "kimi-k2.6")
        assert models.recommend_model(8_000, "anthropic") == ("small", "claude-haiku-4-5")

    def test_unknown_family_falls_back_to_tier(self) -> None:
        assert models.recommend_model(8_000, "nope") == ("small", "small")

    def test_yaml_override(self, proj: Path) -> None:
        (proj / ".forge" / "models.yaml").write_text(
            "myfam:\n  small: x-s\n  mid: x-m\n  frontier: x-f\n", encoding="utf-8")
        assert models.recommend_model(90_000, "myfam") == ("frontier", "x-f")

    def test_cli(self, proj: Path) -> None:
        assert main(["models", "list"]) == 0
        assert main(["models", "recommend", "--tokens", "50000", "--family", "grok"]) == 0


class TestDuration:
    def test_estimate_minutes(self, proj: Path) -> None:
        calibrate.record(5, 5, task_type="r", duration_seconds=1800)  # 30 min
        calibrate.record(5, 5, task_type="r", duration_seconds=2400)  # 40 min
        est = calibrate.estimate_duration("r")
        assert est["n"] == 2 and est["avg_minutes"] == 35.0

    def test_filter_by_type(self, proj: Path) -> None:
        calibrate.record(5, 5, task_type="a", duration_seconds=600)
        calibrate.record(5, 5, task_type="b", duration_seconds=1200)
        assert calibrate.durations("a") == [600.0]

    def test_no_duration_returns_none(self, proj: Path) -> None:
        calibrate.record(5, 5, task_type="r")  # no duration recorded
        assert calibrate.estimate_duration("r") is None

    def test_cli_model_and_duration(self, proj: Path) -> None:
        calibrate.record(50_000, 70_000, task_type="r", duration_seconds=1800)
        assert main(["calibrate", "model", "--type", "r", "--family", "openai"]) == 0
        assert main(["calibrate", "duration", "--type", "r"]) == 0
