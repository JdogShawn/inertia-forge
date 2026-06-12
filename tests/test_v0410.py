"""v0.41.0 — verify-output: detect empty / metadata-only work (an agent that
'finished' a task but changed no real code). Git stubbed for hermeticity.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import gitcheck
from inertia_forge.cli import main


class TestMeaningfulChanges:
    def test_splits_meaningful_from_metadata(self, monkeypatch) -> None:
        def fake_git(root, *args):
            if args[:2] == ("diff", "--name-only"):
                return "src/a.py\nREADME.md\n.forge/x.json\n"
            if args[:2] == ("ls-files", "--others"):
                return "tests/test_b.py\n"
            return ""
        monkeypatch.setattr(gitcheck, "_git", fake_git)
        meaningful, other = gitcheck.meaningful_changes(Path("."), "HEAD")
        assert set(meaningful) == {"src/a.py", "tests/test_b.py"}  # untracked test included
        assert other == ["README.md"]  # .forge churn filtered out

    def test_dedups(self, monkeypatch) -> None:
        monkeypatch.setattr(gitcheck, "_git",
                            lambda root, *a: "src/a.py\n" if a[:2] == ("diff", "--name-only") else "src/a.py\n")
        meaningful, _ = gitcheck.meaningful_changes(Path("."), "HEAD")
        assert meaningful == ["src/a.py"]


class TestCli:
    def test_meaningful_exit_0(self, monkeypatch) -> None:
        monkeypatch.setattr(gitcheck, "meaningful_changes", lambda r, ref: (["src/a.py"], []))
        assert main(["verify-output"]) == 0

    def test_metadata_only_exit_1(self, monkeypatch) -> None:
        monkeypatch.setattr(gitcheck, "meaningful_changes", lambda r, ref: ([], ["README.md"]))
        assert main(["verify-output"]) == 1

    def test_no_changes_exit_1(self, monkeypatch) -> None:
        monkeypatch.setattr(gitcheck, "meaningful_changes", lambda r, ref: ([], []))
        assert main(["verify-output"]) == 1
