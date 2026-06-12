"""v0.36.0 — cross-reference integrity (xref): dangling imports + orphaned tests.
Modelled on paircoder's sweep classifier (orphaned_test / dangling categories).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import xref
from inertia_forge.cli import main


def _pkg(tmp: Path, files: dict[str, str]) -> Path:
    d = tmp / "pkg"
    d.mkdir()
    (d / "__init__.py").write_text("", encoding="utf-8")
    for name, src in files.items():
        (d / name).write_text(src, encoding="utf-8")
    return d


class TestXref:
    def test_dangling_import_flagged(self, tmp_path: Path) -> None:
        _pkg(tmp_path, {"core.py": "def real():\n    return 1\n",
                        "user.py": "from pkg.core import real, gone\n"})
        names = [(n, cat) for _, _, _, n, cat in xref.dangling(tmp_path)]
        assert ("gone", "dangling_import") in names
        assert all(n != "real" for _, _, _, n, _ in xref.dangling(tmp_path))

    def test_orphaned_test_category(self, tmp_path: Path) -> None:
        _pkg(tmp_path, {"core.py": "def real():\n    return 1\n"})
        tdir = tmp_path / "pkg" / "tests"
        tdir.mkdir()
        (tdir / "__init__.py").write_text("", encoding="utf-8")
        (tdir / "test_x.py").write_text("from pkg.core import deleted\n", encoding="utf-8")
        assert any(cat == "orphaned_test" for *_, cat in xref.dangling(tmp_path))

    def test_clean_when_resolves(self, tmp_path: Path) -> None:
        _pkg(tmp_path, {"core.py": "def real():\n    return 1\n",
                        "user.py": "from pkg.core import real\n"})
        assert xref.dangling(tmp_path) == []

    def test_submodule_import_not_flagged(self, tmp_path: Path) -> None:
        _pkg(tmp_path, {"sub.py": "x = 1\n", "user.py": "from pkg import sub\n"})
        assert xref.dangling(tmp_path) == []

    def test_reexport_counts_as_defined(self, tmp_path: Path) -> None:
        # core re-exports `helper` via import → it IS available from core
        _pkg(tmp_path, {"base.py": "def helper():\n    return 1\n",
                        "core.py": "from pkg.base import helper\n",
                        "user.py": "from pkg.core import helper\n"})
        assert xref.dangling(tmp_path) == []

    def test_cli_exit_1(self, tmp_path: Path, monkeypatch) -> None:
        _pkg(tmp_path, {"core.py": "def r():\n    return 1\n",
                        "u.py": "from pkg.core import missing\n"})
        monkeypatch.chdir(tmp_path)
        assert main(["xref", "."]) == 1

    def test_cli_clean(self, tmp_path: Path, monkeypatch) -> None:
        _pkg(tmp_path, {"core.py": "def r():\n    return 1\n"})
        monkeypatch.chdir(tmp_path)
        assert main(["xref", "."]) == 0
