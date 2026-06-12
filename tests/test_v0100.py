"""v0.10.0 — release, gaps, sprint, feedback, install-hook, skill authoring, wizard."""
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


class TestRelease:
    def test_version_consistency(self, proj: Path) -> None:
        from inertia_forge.release import versions_consistent
        (proj / "pyproject.toml").write_text('version = "1.2.3"\n', encoding="utf-8")
        (proj / "src" / "pkg").mkdir(parents=True)
        init = proj / "src" / "pkg" / "__init__.py"
        init.write_text('__version__ = "1.2.3"\n', encoding="utf-8")
        ok, v = versions_consistent()
        assert ok and len(v) == 2
        assert main(["release", "validate-versions"]) == 0
        init.write_text('__version__ = "9.9.9"\n', encoding="utf-8")
        assert versions_consistent()[0] is False
        assert main(["release", "validate-versions"]) == 1


class TestGaps:
    def test_task_gap_detected(self, proj: Path) -> None:
        from inertia_forge.gaps import _task_gaps
        tk.add_task("T1.1", "x", 5, ["a"], "pytest")
        d = tk.load(); d["tasks"]["T1.1"]["verification"] = ""; tk.save(d)
        assert any("verification" in g for g in _task_gaps())

    def test_test_coverage_gap(self, proj: Path) -> None:
        from inertia_forge.gaps import _test_gaps
        (proj / "pkg").mkdir(); (proj / "pkg" / "thing.py").write_text("x=1\n", encoding="utf-8")
        assert any("thing" in g for g in _test_gaps(proj / "pkg"))


class TestSprint:
    def test_lifecycle(self, proj: Path) -> None:
        from inertia_forge import sprint
        sprint.start("s1")
        assert sprint.add_task("T1.1") is True
        d = sprint._load()
        assert d["active"] == "s1" and "T1.1" in d["sprints"]["s1"]["tasks"]
        assert sprint.complete() is True
        assert sprint._load()["sprints"]["s1"]["done"] is True
        assert main(["sprint", "list"]) == 0


class TestFeedback:
    def test_add_list(self, proj: Path, capsys) -> None:
        assert main(["feedback", "add", "prefer smaller PRs", "--kind", "preference"]) == 0
        assert main(["feedback", "list"]) == 0
        assert "smaller PRs" in capsys.readouterr().out


class TestInstallHook:
    def test_writes_git_hook(self, proj: Path) -> None:
        (proj / ".git").mkdir()
        assert main(["install-hook"]) == 0
        hook = proj / ".git" / "hooks" / "pre-commit"
        assert hook.exists() and "inertia-forge check" in hook.read_text(encoding="utf-8")

    def test_not_a_repo(self, proj: Path) -> None:
        assert main(["install-hook"]) == 1


class TestSkillAuthoring:
    def test_new_and_score(self, proj: Path) -> None:
        from inertia_forge import skill_authoring as sa
        path = sa.new("my_thing")
        assert path.exists() and path.name == "SKILL.md"
        pts, total, _ = sa.score("implementing_with_tdd")
        assert 0 < pts <= total
        assert main(["skills", "score", "implementing_with_tdd"]) in (0, 1)


class TestWizard:
    def test_runs(self, tmp_path: Path) -> None:
        assert main(["wizard", "--target", str(tmp_path)]) == 0
        assert (tmp_path / ".claude" / "agents").is_dir()
