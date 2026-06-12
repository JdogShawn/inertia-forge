"""v0.45.0 — project health report: one markdown page unifying the scan battery,
code-quality metrics, and task progress. Deterministic, ASCII-clean.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import report, tasks as t
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    src = tmp_path / "src"
    src.mkdir()
    (src / "m.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    return tmp_path


class TestReport:
    def test_has_battery_and_quality_sections(self, proj: Path) -> None:
        out = report.build_report("src")
        assert "Project Health Report" in out
        assert "Quality battery" in out and "| analyzer | result |" in out
        assert "## Code quality" in out and "docstring_pct" in out

    def test_includes_task_progress(self, proj: Path) -> None:
        t.add_task("T1.1", "x", 1, ["a"], "pytest")
        out = report.build_report("src")
        assert "## Tasks" in out and "0/1 tasks done" in out

    def test_ascii_clean(self, proj: Path) -> None:
        report.build_report("src").encode("ascii")  # raises if any non-ASCII slipped in

    def test_cli(self, proj: Path) -> None:
        assert main(["report", "--path", "src"]) == 0
