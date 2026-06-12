"""v0.26.0 — conventional-commit changelog from git history. Pure parsing/render;
git stubbed for the CLI.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import changelog
from inertia_forge.cli import main


class TestParse:
    def test_groups_by_type_and_scope(self) -> None:
        grouped, breaking = changelog.parse_commits([
            "feat(api): add endpoint", "fix: correct bug", "docs: update readme"])
        assert grouped["feat"] == ["api: add endpoint"]
        assert grouped["fix"] == ["correct bug"]
        assert grouped["docs"] == ["update readme"]
        assert breaking == []

    def test_breaking_flagged(self) -> None:
        grouped, breaking = changelog.parse_commits(["feat!: drop python 3.9",
                                                     "refactor(core)!: rename API"])
        assert breaking == ["drop python 3.9", "core: rename API"]
        assert "drop python 3.9" in grouped["feat"]

    def test_non_conventional_goes_to_other(self) -> None:
        grouped, _ = changelog.parse_commits(["WIP messy commit", "Merge branch x"])
        assert grouped["other"] == ["WIP messy commit", "Merge branch x"]


class TestRender:
    def test_sections_and_order(self) -> None:
        grouped = {"feat": ["a"], "fix": ["b"], "other": ["c"]}
        out = changelog.render(grouped, breaking=[])
        assert "## Features" in out and "## Fixes" in out and "## Other" in out
        assert out.index("Features") < out.index("Fixes") < out.index("Other")

    def test_breaking_first(self) -> None:
        out = changelog.render({"feat": ["x"]}, breaking=["big change"])
        assert out.index("Breaking changes") < out.index("Features")

    def test_ascii_clean(self) -> None:
        changelog.render({"feat": ["x"]}, breaking=["y"]).encode("ascii")


class TestCli:
    def test_renders_from_git(self, tmp_path: Path, monkeypatch, capsys) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(changelog, "git_subjects",
                            lambda root, rng: ["feat: a thing", "fix: a bug"])
        monkeypatch.setattr(changelog, "_git", lambda root, *a: "v1.0.0")
        assert main(["changelog"]) == 0
        out = capsys.readouterr().out
        assert "Features" in out and "a thing" in out

    def test_empty_range(self, tmp_path: Path, monkeypatch, capsys) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(changelog, "git_subjects", lambda root, rng: [])
        monkeypatch.setattr(changelog, "_git", lambda root, *a: "")
        assert main(["changelog"]) == 0
        assert "no commits" in capsys.readouterr().out
