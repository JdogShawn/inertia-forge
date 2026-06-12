"""v0.22.0 — cyclomatic (McCabe) complexity. Pure AST; synthetic functions for
exact, deterministic assertions.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from inertia_forge import complexity
from inertia_forge.cli import main


def _cx(src: str) -> int:
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
    return complexity.complexity_of(fn)


class TestComplexity:
    def test_straight_line_is_one(self) -> None:
        assert _cx("def f():\n    return 1\n") == 1

    def test_if_adds_one(self) -> None:
        assert _cx("def f(x):\n    if x:\n        return 1\n    return 0\n") == 2

    def test_boolops_add_per_operand(self) -> None:
        assert _cx("def f(a, b, c):\n    return a and b and c\n") == 3  # 1 + (3-1)

    def test_comprehension_if(self) -> None:
        assert _cx("def f(x):\n    return [i for i in x if i]\n") == 2

    def test_loops_and_except(self) -> None:
        src = ("def f(x):\n    for i in x:\n        while i:\n            i -= 1\n"
               "    try:\n        pass\n    except ValueError:\n        pass\n")
        assert _cx(src) == 4  # 1 + for + while + except

    def test_match_cases(self) -> None:
        src = "def f(x):\n    match x:\n        case 1:\n            pass\n        case _:\n            pass\n"
        assert _cx(src) == 3  # 1 + 2 cases

    def test_nested_def_scored_separately(self) -> None:
        src = ("def outer(x):\n    def inner(y):\n        if y:\n            return 1\n"
               "    if x:\n        return 2\n")
        assert _cx(src) == 2  # outer's own `if` only; inner not counted


class TestCli:
    def test_analyze_file(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text("def a():\n    return 1\ndef b(x):\n    return x and x or x\n", encoding="utf-8")
        scored = {name: c for name, c, _ in complexity.analyze_file(f)}
        assert scored == {"a": 1, "b": 3}

    def test_exit_codes(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text("def simple():\n    return 1\n", encoding="utf-8")
        assert main(["complexity", str(f), "--max", "10"]) == 0
        f.write_text("def m(x):\n    if x and x:\n        for i in x:\n            pass\n", encoding="utf-8")
        assert main(["complexity", str(f), "--max", "2"]) == 1
