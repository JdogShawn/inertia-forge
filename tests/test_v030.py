"""v0.3.0 deterministic capabilities: metrics, intent, engage, orchestrate, benchmark."""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import tasks as tk
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestMetrics:
    def test_add_total_and_cost(self, proj: Path, capsys) -> None:
        from inertia_forge import metrics as m
        assert main(["metrics", "add", "--in", "1000000", "--out", "500000", "--model", "x"]) == 0
        assert m.totals() == {"x": {"in": 1_000_000, "out": 500_000}}
        assert main(["metrics", "set-rate", "x", "--in", "10", "--out", "30"]) == 0
        assert main(["metrics", "report"]) == 0
        out = capsys.readouterr().out
        assert "$" in out  # 1M*$10 + 0.5M*$30 = $25 estimated


class TestIntent:
    @pytest.mark.parametrize("text,expected", [
        ("fix the broken login crash", "bugfix"),
        ("add a brand new feature", "feature"),
        ("refactor and clean up dead code", "refactor"),
        ("cut a release and bump version", "chore"),
    ])
    def test_classify(self, text: str, expected: str) -> None:
        from inertia_forge.intent import classify
        assert classify(text)["type"] == expected


class TestIgnite:
    def test_ingest_backlog(self, proj: Path) -> None:
        backlog = proj / "backlog.md"
        backlog.write_text(
            "# Checkout v2\ntype: feature\n\n"
            "## T1.1: Cart totals\ncomplexity: 8\n- [ ] totals correct\n- [ ] tests pass\n"
            "verify: pytest tests/cart\n\n"
            "## T1.2: Tax\ncomplexity: 3\n- [ ] tax computed\nverify: pytest tests/tax\n",
            encoding="utf-8",
        )
        assert main(["ignite", str(backlog)]) == 0
        ids = [t["id"] for t in tk.list_tasks()]
        assert ids == ["T1.1", "T1.2"]
        assert tk.get_plan()["title"] == "Checkout v2"
        assert len(tk.get_task("T1.1")["acceptance_criteria"]) == 2


class TestOrchestrate:
    def test_passes_when_all_steps_pass(self, proj: Path) -> None:
        assert main(["orchestrate", "skills validate"]) == 0

    def test_fails_fast(self, proj: Path) -> None:
        f = proj / "many.py"
        f.write_text("".join(f"def f{i}(): pass\n" for i in range(16)), encoding="utf-8")
        # first step fails (P0) -> pipeline returns non-zero, second never runs.
        # Use a forward-slash path: shlex (POSIX) eats backslashes cross-platform.
        assert main(["orchestrate", f"arch {f.as_posix()}", "skills validate"]) == 1


class TestBenchmark:
    def test_runs(self, proj: Path) -> None:
        (proj / "m.py").write_text("x = 1\n", encoding="utf-8")
        assert main(["benchmark", str(proj), "--runs", "1"]) == 0
