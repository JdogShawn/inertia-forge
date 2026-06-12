"""v0.16.0 — git-aware verification, change-scope enforcement, context freshness,
deterministic token estimation. All offline; git calls are stubbed for hermeticity.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import freshness, gitcheck, scope, tokens
from inertia_forge import tasks as t
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestGitCheck:
    def test_dirty_filters_churn(self, monkeypatch) -> None:
        monkeypatch.setattr(gitcheck, "_git",
                            lambda root, *a: " M src/a.py\n?? .forge/x.json\n M .coverage\n")
        assert gitcheck.dirty_files(Path(".")) == ["src/a.py"]

    def test_head_task_extraction(self, monkeypatch) -> None:
        monkeypatch.setattr(gitcheck, "head_subject", lambda root: "feat(T12.3): thing")
        assert gitcheck.head_task(Path(".")) == "T12.3"

    def test_verify_flags_dirty_and_missing_task(self, monkeypatch) -> None:
        monkeypatch.setattr(gitcheck, "dirty_files", lambda root: ["x.py"])
        monkeypatch.setattr(gitcheck, "_git", lambda root, *a: "deadbeef")
        monkeypatch.setattr(gitcheck, "head_subject", lambda root: "no task here")
        issues = gitcheck.verify(Path("."), require_task=True)
        assert len(issues) == 2

    def test_clean_passes(self, monkeypatch) -> None:
        monkeypatch.setattr(gitcheck, "dirty_files", lambda root: [])
        assert gitcheck.verify(Path("."), require_task=False) == []

    def test_cli(self, proj, monkeypatch, capsys) -> None:
        monkeypatch.setattr(gitcheck, "dirty_files", lambda root: [])
        assert main(["verify-commit"]) == 0


class TestTokens:
    def test_estimate_text_blend(self) -> None:
        assert tokens.estimate_text("") == 0
        assert tokens.estimate_text("a" * 40) == 10  # chars/4 dominates
        assert tokens.estimate_text("word " * 10) >= 13  # words×1.3

    def test_estimate_file_and_cli(self, proj, capsys) -> None:
        (proj / "f.txt").write_text("hello world " * 100, encoding="utf-8")
        assert tokens.estimate_file(proj / "f.txt") > 0
        assert main(["tokens", str(proj / "f.txt"), "--quiet"]) == 0
        assert "tokens estimated" in capsys.readouterr().out


class TestFreshness:
    def test_missing_is_stale(self, proj) -> None:
        assert freshness.is_stale(proj / "nope.md") is True

    def test_age_threshold(self, proj) -> None:
        f = proj / "x.md"
        f.write_text("hi", encoding="utf-8")
        mtime = f.stat().st_mtime
        assert freshness.is_stale(f, days=7, now=mtime + 60) is False
        assert freshness.is_stale(f, days=7, now=mtime + 8 * 86400) is True

    def test_stale_files_lists_missing(self, proj) -> None:
        stale = freshness.stale_files(proj)
        assert "CLAUDE.md" in stale  # missing -> stale

    def test_cli(self, proj) -> None:
        assert main(["freshness"]) == 0


class TestScope:
    def test_in_scope_prefix_and_glob(self) -> None:
        assert scope.in_scope("src/a/b.py", ["src/"]) is True
        assert scope.in_scope("docs/x.md", ["src/"]) is False
        assert scope.in_scope("src/a.py", ["src/*.py"]) is True

    def test_out_of_scope(self) -> None:
        changed = ["src/a.py", "other/b.py"]
        assert scope.out_of_scope(changed, ["src/"]) == ["other/b.py"]
        assert scope.out_of_scope(changed, []) == []  # no scope = no enforcement

    def test_set_and_check(self, proj, monkeypatch, capsys) -> None:
        t.add_task("T1.1", "x", 3, ["a"], "pytest")
        t.start_task("T1.1")
        assert main(["scope", "set", "T1.1", "--paths", "src/"]) == 0
        assert t.get_task("T1.1")["scope"] == ["src/"]
        monkeypatch.setattr(scope, "_changed", lambda root: ["src/ok.py", "bad.py"])
        assert main(["scope", "check"]) == 1
        assert "bad.py" in capsys.readouterr().out
