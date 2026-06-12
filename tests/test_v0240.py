"""v0.24.0 — docstring coverage (the documentation analog of test coverage).
Pure AST; synthetic sources for exact assertions.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from inertia_forge import docstrings
from inertia_forge.cli import main

_SRC = '''
def documented():
    """Doc."""
    return 1

def undocumented(x):
    return x

def _private():
    return 1

class Thing:
    """A class doc."""
    def method(self):
        return 2

    def _hidden(self):
        return 3
'''


class TestDocstrings:
    def test_documentables_skips_private(self) -> None:
        tree = ast.parse(_SRC)
        names = [n for n, _ in docstrings._documentables(tree)]
        assert names == ["documented", "undocumented", "Thing", "Thing.method"]

    def test_analyze_file_marks_docstrings(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text(_SRC, encoding="utf-8")
        got = dict(docstrings.analyze_file(f))
        assert got == {"documented": True, "undocumented": False,
                       "Thing": True, "Thing.method": False}

    def test_collect_excludes_tests(self, tmp_path: Path) -> None:
        (tmp_path / "src.py").write_text("def a():\n    pass\n", encoding="utf-8")
        (tmp_path / "test_x.py").write_text("def b():\n    pass\n", encoding="utf-8")
        tdir = tmp_path / "tests"
        tdir.mkdir()
        (tdir / "c.py").write_text("def c():\n    pass\n", encoding="utf-8")
        names = [str(f.name) for f in docstrings._collect(str(tmp_path))]
        assert names == ["src.py"]

    def test_cli_gate(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text(_SRC, encoding="utf-8")
        assert main(["docs", str(f), "--min", "80"]) == 1   # 50% < 80
        assert main(["docs", str(f), "--min", "40"]) == 0   # 50% >= 40

    def test_cli_no_symbols(self, tmp_path: Path) -> None:
        (tmp_path / "m.py").write_text("x = 1\n", encoding="utf-8")
        assert main(["docs", str(tmp_path)]) == 0
