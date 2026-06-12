"""v0.23.0 — module import graph + circular-import detection, with hard
(import-time) vs soft (lazy, in-function) edge classification. Hermetic synthetic
packages.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import importgraph
from inertia_forge.cli import main


def _pkg(tmp: Path, files: dict[str, str]) -> Path:
    d = tmp / "pkg"
    d.mkdir()
    (d / "__init__.py").write_text("", encoding="utf-8")
    for name, src in files.items():
        (d / name).write_text(src, encoding="utf-8")
    return d


class TestGraph:
    def test_match(self) -> None:
        ms = {"pkg", "pkg.a", "pkg.sub.mod"}
        assert importgraph._match("pkg.a", "pkg", ms) == "pkg.a"
        assert importgraph._match("pkg.sub.mod", "pkg", ms) == "pkg.sub.mod"
        assert importgraph._match("other", "pkg", ms) is None

    def test_from_pkg_import_submodule_edges_to_submodule(self, tmp_path: Path) -> None:
        d = _pkg(tmp_path, {"a.py": "from pkg import b\n", "b.py": "x = 1\n"})
        graph = importgraph.build_graph(d)
        assert graph["pkg.a"] == {"pkg.b"}  # edge to submodule, NOT the package

    def test_hard_cycle_detected(self, tmp_path: Path) -> None:
        d = _pkg(tmp_path, {"a.py": "from pkg import b\n", "b.py": "from pkg import a\n"})
        cyc = importgraph.find_cycle(importgraph.build_graph(d))
        assert cyc and cyc[0] == cyc[-1] and "pkg.a" in cyc

    def test_soft_edge_breaks_hard_cycle(self, tmp_path: Path) -> None:
        d = _pkg(tmp_path, {
            "a.py": "from pkg import b\n",
            "b.py": "def f():\n    from pkg import a\n    return a\n"})
        assert importgraph.find_cycle(importgraph.build_graph(d, soft=False)) is None
        assert importgraph.find_cycle(importgraph.build_graph(d, soft=True)) is not None

    def test_no_self_edges(self, tmp_path: Path) -> None:
        d = _pkg(tmp_path, {"a.py": "import pkg.a\n"})
        assert importgraph.build_graph(d)["pkg.a"] == set()


class TestCli:
    def test_hard_cycle_exits_1(self, tmp_path: Path, monkeypatch) -> None:
        _pkg(tmp_path, {"a.py": "from pkg import b\n", "b.py": "from pkg import a\n"})
        monkeypatch.chdir(tmp_path)
        assert main(["imports", "."]) == 1

    def test_clean_exits_0(self, tmp_path: Path, monkeypatch) -> None:
        _pkg(tmp_path, {"a.py": "x = 1\n", "b.py": "from pkg import a\n"})
        monkeypatch.chdir(tmp_path)
        assert main(["imports", "."]) == 0

    def test_soft_cycle_is_advisory_exit_0(self, tmp_path: Path, monkeypatch, capsys) -> None:
        _pkg(tmp_path, {
            "a.py": "from pkg import b\n",
            "b.py": "def f():\n    from pkg import a\n    return a\n"})
        monkeypatch.chdir(tmp_path)
        assert main(["imports", "."]) == 0
        assert "soft cycle" in capsys.readouterr().out
