"""v0.15.0 — INERTIA task-intelligence layer: dependency graph (ready/blocked/
waves/cycles), complexity heuristic, consistency audit, file-role detector,
targeted-test selection, config presets. All deterministic, zero deps.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import (consistency, estimate, palette, roles, targeted,
                           taskgraph as tg, tasks as t)
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


def _chain(proj: Path) -> None:
    t.add_task("T1.1", "design", 5, ["a"], "pytest")
    t.add_task("T1.2", "build", 3, ["b"], "pytest", depends_on=["T1.1"])
    t.add_task("T1.3", "ship", 3, ["c"], "pytest", depends_on=["T1.2"])


class TestGraph:
    def test_ready_is_only_unblocked(self, proj: Path) -> None:
        _chain(proj)
        assert [x["id"] for x in tg.ready_tasks()] == ["T1.1"]

    def test_blocked_maps_to_blockers(self, proj: Path) -> None:
        _chain(proj)
        assert tg.blocked_tasks() == {"T1.2": ["T1.1"], "T1.3": ["T1.2"]}

    def test_waves_and_topo(self, proj: Path) -> None:
        _chain(proj)
        assert tg.parallel_waves() == [["T1.1"], ["T1.2"], ["T1.3"]]
        assert tg.topo_order() == ["T1.1", "T1.2", "T1.3"]

    def test_completing_dep_unblocks(self, proj: Path) -> None:
        _chain(proj)
        t.check_ac("T1.1", 0); t.complete_task("T1.1")
        assert [x["id"] for x in tg.ready_tasks()] == ["T1.2"]

    def test_cycle_detected(self, proj: Path) -> None:
        _chain(proj)
        t.update_task("T1.1", depends_on=["T1.3"])
        cyc = tg.find_cycle()
        assert cyc and cyc[0] == cyc[-1] and "T1.2" in cyc

    def test_missing_deps(self, proj: Path) -> None:
        t.add_task("T2.1", "x", 1, ["a"], "pytest", depends_on=["T9.9"])
        assert tg.missing_deps() == {"T2.1": ["T9.9"]}

    def test_next_task_respects_deps(self, proj: Path) -> None:
        _chain(proj)
        assert t.next_task()["id"] == "T1.1"  # not T1.2/T1.3 (blocked)


class TestEstimate:
    def test_scales_with_ac_and_signal(self, proj: Path) -> None:
        t.add_task("T1.1", "refactor core", 0, ["a", "b"], "x && y")
        # 1 + 2*1.5 + 2(multi-verify) + 3(refactor) = 9
        assert estimate.estimate(t.get_task("T1.1")) == 9.0

    def test_cli_apply_writes(self, proj: Path) -> None:
        t.add_task("T1.1", "add thing", 0, ["a"], "pytest")
        assert main(["task", "estimate", "T1.1", "--apply"]) == 0
        assert t.get_task("T1.1")["complexity"] > 0


class TestConsistency:
    def test_clean_store_passes(self, proj: Path) -> None:
        _chain(proj)
        assert consistency.issues() == []
        assert main(["consistency"]) == 0

    def test_self_dep_and_missing_flagged(self, proj: Path) -> None:
        t.add_task("T1.1", "x", 1, ["a"], "pytest", depends_on=["T1.1", "T9.9"])
        found = " ".join(consistency.issues())
        assert "itself" in found and "missing task T9.9" in found
        assert main(["consistency"]) == 1

    def test_audit_subcommand(self, proj: Path) -> None:
        _chain(proj)
        assert main(["task", "audit"]) == 0


class TestRoles:
    def test_classifies(self) -> None:
        assert roles.detect("tests/test_x.py") == "test"
        assert roles.detect("pkg/cli.py") == "cli"
        assert roles.detect("pyproject.toml") == "config"
        assert roles.detect("README.md") == "doc"
        assert roles.detect("data/rows.csv") == "data"
        assert roles.detect("pkg/service.py") == "source"

    def test_cli(self, capsys) -> None:
        assert main(["role", "tests/test_a.py", "a/b.py"]) == 0
        assert "test" in palette.strip_ansi(capsys.readouterr().out)


class TestTargeted:
    def test_candidates_skip_non_source(self) -> None:
        assert targeted.candidates("tests/test_x.py") == []
        assert targeted.candidates("pkg/__init__.py") == []
        assert "tests/test_foo.py" in targeted.candidates("src/pkg/foo.py")

    def test_existing_targets(self, proj: Path) -> None:
        (proj / "tests").mkdir()
        (proj / "tests" / "test_foo.py").write_text("# t", encoding="utf-8")
        assert targeted.existing_targets(["src/pkg/foo.py"], proj) == ["tests/test_foo.py"]


class TestPresets:
    def test_list_and_apply(self, proj: Path, capsys) -> None:
        assert main(["preset", "list"]) == 0
        assert "library" in capsys.readouterr().out
        assert main(["preset", "apply", "service"]) == 0
        from inertia_forge import config
        assert config.get("target") == "app/"

    def test_unknown_preset(self, proj: Path) -> None:
        assert main(["preset", "show", "nope"]) == 1
