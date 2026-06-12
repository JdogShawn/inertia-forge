"""v0.19.0 — project-wide dead-symbol detection + deterministic insight synthesis.
Both pure/deterministic; dead-code runs over controlled trees for hermeticity.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import deadcode, learn
from inertia_forge.cli import main


class TestDeadCode:
    def test_flags_only_unreferenced_non_kept(self, tmp_path: Path) -> None:
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "a.py").write_text(
            "def used():\n    return 1\n"
            "def dead():\n    return 2\n"
            "def _priv():\n    return 3\n"
            "def run_cli():\n    return used()\n"
            "class Dunder:\n    def __init__(self):\n        pass\n",
            encoding="utf-8")
        (pkg / "b.py").write_text("from pkg.a import used\nused()\n", encoding="utf-8")
        names = [d[0] for d in deadcode.find_dead(tmp_path)]
        assert "dead" in names
        assert "used" not in names       # referenced in b.py
        assert "_priv" not in names      # underscore kept
        assert "run_cli" not in names    # run_ entrypoint kept

    def test_attribute_reference_counts(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("def helper():\n    return 1\n", encoding="utf-8")
        (tmp_path / "b.py").write_text("import a\na.helper()\n", encoding="utf-8")
        assert "helper" not in [d[0] for d in deadcode.find_dead(tmp_path)]

    def test_dunder_all_export_counts(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text(
            "def api():\n    return 1\n__all__ = ['api']\n", encoding="utf-8")
        assert "api" not in [d[0] for d in deadcode.find_dead(tmp_path)]

    def test_test_files_excluded_as_def_sources(self, tmp_path: Path) -> None:
        (tmp_path / "src.py").write_text("def helper():\n    return 1\n", encoding="utf-8")
        tdir = tmp_path / "tests"
        tdir.mkdir()
        (tdir / "test_x.py").write_text("def fixture():\n    return 1\nhelper()\n", encoding="utf-8")
        names = [d[0] for d in deadcode.find_dead(tmp_path)]
        assert "helper" not in names    # referenced by a test
        assert "fixture" not in names    # defined in a test file -> not a def source

    def test_cli_strict_exit(self, tmp_path: Path, monkeypatch) -> None:
        (tmp_path / "a.py").write_text("def orphan():\n    return 1\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert main(["dead-code", "."]) == 0           # advisory by default
        assert main(["dead-code", ".", "--strict"]) == 1


class TestSynthesize:
    @pytest.fixture()
    def proj(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".forge").mkdir()
        return tmp_path

    def test_clusters_by_tag_frequency(self, proj: Path) -> None:
        learn.add("alpha", ["x"]); learn.add("beta", ["x"])
        learn.add("gamma", ["y"]); learn.add("delta", [])
        clusters = dict(learn.synthesize())
        assert clusters["x"] == ["alpha", "beta"]
        assert clusters["y"] == ["gamma"]
        assert clusters["(untagged)"] == ["delta"]
        assert learn.synthesize()[0][0] == "x"  # most frequent first

    def test_cli(self, proj: Path, capsys) -> None:
        learn.add("note", ["topic"])
        assert main(["learn", "synthesize"]) == 0
        assert "topic (1)" in capsys.readouterr().out
