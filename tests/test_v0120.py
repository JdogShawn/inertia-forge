"""v0.12.0 — task lifecycle (next/archive/restore/cleanup/changelog),
metrics velocity/summary, compaction snapshot/recover, orchestrate select-agent,
budget gate, config validate. All deterministic; no network, no LLM.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import tasks as t
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


def _done_task(tid: str) -> None:
    t.add_task(tid, f"title {tid}", 5, ["a"], "pytest")
    t.start_task(tid)
    t.check_ac(tid, 0)
    t.complete_task(tid)


class TestLifecycle:
    def test_next_prefers_in_progress_then_pending(self, proj: Path) -> None:
        t.add_task("T1.1", "first", 3, ["a"], "pytest")
        t.add_task("T1.2", "second", 3, ["a"], "pytest")
        assert t.next_task()["id"] == "T1.1"  # first pending
        t.start_task("T1.2")
        assert t.next_task()["id"] == "T1.2"  # active in_progress wins

    def test_complete_stamps_completed_at(self, proj: Path) -> None:
        _done_task("T1.1")
        assert t.get_task("T1.1")["completed_at"].endswith("+00:00") or \
            "T" in t.get_task("T1.1")["completed_at"]

    def test_archive_restore_roundtrip(self, proj: Path) -> None:
        t.add_task("T1.1", "x", 5, ["a"], "pytest")
        assert t.archive_task("T1.1") is True
        assert t.get_task("T1.1") is None
        assert [x["id"] for x in t.list_archived()] == ["T1.1"]
        assert t.restore_task("T1.1") is True
        assert t.get_task("T1.1")["id"] == "T1.1"

    def test_archive_missing_returns_false(self, proj: Path) -> None:
        assert t.archive_task("T9.9") is False
        assert t.restore_task("T9.9") is False

    def test_cleanup_archives_done_only(self, proj: Path) -> None:
        _done_task("T1.1")
        t.add_task("T1.2", "pending one", 3, ["a"], "pytest")
        assert t.cleanup_done() == 1
        assert [x["id"] for x in t.list_tasks()] == ["T1.2"]
        assert [x["id"] for x in t.list_archived()] == ["T1.1"]

    def test_cli_changelog_includes_archived(self, proj: Path, capsys) -> None:
        _done_task("T1.1")
        t.cleanup_done()
        assert main(["task", "changelog"]) == 0
        out = capsys.readouterr().out
        assert "Changelog" in out and "T1.1" in out

    def test_cli_next_and_list_archived(self, proj: Path) -> None:
        t.add_task("T1.1", "x", 5, ["a"], "pytest")
        assert main(["task", "next"]) == 0
        assert main(["task", "list-archived"]) == 0


class TestMetricsAnalytics:
    def test_velocity_counts_completed(self, proj: Path) -> None:
        from inertia_forge.metrics import _completed_tasks
        _done_task("T1.1")
        _done_task("T1.2")
        assert len(_completed_tasks()) == 2

    def test_cli_velocity_and_summary(self, proj: Path) -> None:
        _done_task("T1.1")
        assert main(["metrics", "velocity"]) == 0
        assert main(["metrics", "summary"]) == 0


class TestCompaction:
    def test_snapshot_then_recover(self, proj: Path, capsys) -> None:
        t.create_plan("feature", "demo")
        assert main(["compaction", "snapshot"]) == 0
        snaps = list((proj / ".forge" / "snapshots").glob("snapshot_*.md"))
        assert len(snaps) == 1
        capsys.readouterr()
        assert main(["compaction", "recover"]) == 0
        assert "Forge Context Pack" in capsys.readouterr().out

    def test_check_and_cleanup(self, proj: Path) -> None:
        assert main(["compaction", "check"]) == 0  # nothing yet
        main(["compaction", "snapshot"])
        main(["compaction", "snapshot"])
        assert len(list((proj / ".forge" / "snapshots").glob("*.md"))) == 2
        assert main(["compaction", "cleanup", "--keep", "1"]) == 0
        assert len(list((proj / ".forge" / "snapshots").glob("*.md"))) == 1


class TestSelectAgentAndGates:
    def test_orchestrate_select_agent(self, proj: Path, capsys) -> None:
        assert main(["orchestrate", "select-agent", "write a failing test first"]) == 0
        assert "agent:" in capsys.readouterr().out

    def test_budget_max_gate(self, proj: Path) -> None:
        t.add_task("T1.1", "x", 80, ["a"], "pytest")
        assert main(["task", "budget", "--max", "50"]) == 1   # over
        assert main(["task", "budget", "--max", "100"]) == 0  # within

    def test_config_validate(self, proj: Path, capsys) -> None:
        assert main(["config", "set", "target", "src/"]) == 0
        assert main(["config", "validate"]) == 0
        main(["config", "set", "weird_key", "1"])
        capsys.readouterr()
        assert main(["config", "validate"]) == 0
        assert "unknown" in capsys.readouterr().out
