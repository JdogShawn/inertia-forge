"""v0.25.0 — type-hint coverage (the typing analog of test/docstring coverage).
Pure AST; synthetic sources for exact assertions.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import typehints
from inertia_forge.cli import main

_SRC = '''
def fully(x: int, y: str) -> bool:
    return True

def no_return(x: int):
    return x

def no_param(x) -> int:
    return 1

def nothing():
    return 0

class C:
    def method(self, a: int) -> None:
        pass

    def untyped_method(self, a):
        pass
'''


class TestTypeHints:
    def test_fully_typed(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text(_SRC, encoding="utf-8")
        got = dict(typehints.analyze_file(f))
        assert got["fully"] is True
        assert got["no_return"] is False        # missing return annotation
        assert got["no_param"] is False         # missing param annotation
        assert got["nothing"] is False          # no return annotation
        assert got["C.method"] is True          # self excluded, a + return typed
        assert got["C.untyped_method"] is False

    def test_no_args_needs_return(self, tmp_path: Path) -> None:
        f = tmp_path / "n.py"
        f.write_text("def f() -> int:\n    return 1\n", encoding="utf-8")
        assert dict(typehints.analyze_file(f))["f"] is True

    def test_self_not_required_typed(self, tmp_path: Path) -> None:
        f = tmp_path / "c.py"
        f.write_text("class K:\n    def m(self) -> int:\n        return 1\n", encoding="utf-8")
        assert dict(typehints.analyze_file(f))["K.m"] is True

    def test_cli_gate(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text(_SRC, encoding="utf-8")
        # 2 typed of 6 -> 33.3%
        assert main(["types", str(f), "--min", "80"]) == 1
        assert main(["types", str(f), "--min", "30"]) == 0
