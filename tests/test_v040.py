"""v0.4.0 — full (not thin) deterministic commands: config, feature, learn, standup."""
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


class TestConfig:
    def test_set_get_types_unset(self, proj: Path) -> None:
        from inertia_forge import config as cfg
        assert main(["config", "set", "default_target", "src"]) == 0
        assert cfg.get("default_target") == "src"
        assert main(["config", "set", "default_complexity", "8"]) == 0
        assert cfg.get("default_complexity") == 8           # coerced to int
        assert main(["config", "set", "strict", "true"]) == 0
        assert cfg.get("strict") is True                    # coerced to bool
        assert main(["config", "list"]) == 0
        assert main(["config", "unset", "strict"]) == 0
        assert cfg.get("strict") is None


class TestFeature:
    def test_scaffold_no_branch(self, proj: Path) -> None:
        assert main(["feature", "cool thing", "--no-branch"]) == 0
        assert tk.get_plan()["title"] == "Feature: cool thing"
        assert tk.get_task("T1.1") is not None
        from inertia_forge import state as st
        assert "cool thing" in st.load()["next"]

    def test_respects_default_complexity(self, proj: Path) -> None:
        from inertia_forge import config as cfg
        cfg.set_value("default_complexity", 13)
        main(["feature", "x", "--no-branch"])
        assert tk.get_task("T1.1")["complexity"] == 13


class TestLearn:
    def test_add_list_search_shorthand(self, proj: Path) -> None:
        from inertia_forge import learn
        assert main(["learn", "add", "use forward slashes", "--tag", "win"]) == 0
        assert main(["learn", "shlex eats backslashes"]) == 0   # shorthand add
        assert len(learn.all_entries()) == 2
        assert len(learn.search("forward")) == 1                # text match (unambiguous)
        assert len(learn.search("win")) == 1                    # tag match
        assert main(["learn", "list"]) == 0


class TestStandup:
    def test_runs(self, proj: Path, capsys) -> None:
        tk.create_plan("feature", "Demo")
        tk.add_task("T1.1", "x", 5, ["a"], "pytest")
        tk.start_task("T1.1")
        assert main(["standup"]) == 0
        out = capsys.readouterr().out
        assert "## Tasks" in out and "in progress" in out
