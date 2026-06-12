"""v0.33.0 (enriched v0.39.0) — module split adviser. Threshold-gated, class-aware
(cross-referenced to paircoder's SplitAnalyzer: line threshold + class/function
components).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import splitter
from inertia_forge.cli import main

_SRC = "\n".join(
    [f"def check_{i}(x):\n    return x\n" for i in range(4)]
    + [f"def run_{i}(x):\n    return x\n" for i in range(4)]
    + ["def lonely(x):\n    return x\n"])


class TestSuggest:
    def test_clusters_function_prefixes(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text(_SRC, encoding="utf-8")
        sugg = splitter.suggest(f, threshold=0)
        labels = {label for label, *_ in sugg}
        assert "check" in labels and "run" in labels
        check = next(s for s in sugg if s[0] == "check")
        assert check[1] == "functions" and len(check[2]) == 4

    def test_classes_are_components(self, tmp_path: Path) -> None:
        f = tmp_path / "c.py"
        f.write_text("class Foo:\n    pass\nclass Bar:\n    def m(self):\n        return 1\n",
                     encoding="utf-8")
        kinds = {(label, kind) for label, kind, *_ in splitter.suggest(f, threshold=0)}
        assert ("Foo", "class") in kinds and ("Bar", "class") in kinds

    def test_threshold_gate(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text(_SRC, encoding="utf-8")  # ~18 lines
        assert splitter.suggest(f, threshold=1000) == []  # under threshold → left alone
        assert splitter.suggest(f, threshold=0)            # over threshold → components

    def test_small_file_default_threshold(self, tmp_path: Path) -> None:
        f = tmp_path / "s.py"
        f.write_text("def a():\n    pass\n", encoding="utf-8")
        assert splitter.suggest(f) == []  # default 300, tiny file

    def test_dest_module(self) -> None:
        assert splitter._dest_module("m", "_check", "functions") == "m_checks.py"
        assert splitter._dest_module("m", "run", "functions") == "m_commands.py"
        assert splitter._dest_module("m", "MyClass", "class") == "m_myclass.py"


class TestCli:
    def test_advisory_exit_0(self, tmp_path: Path, capsys) -> None:
        f = tmp_path / "m.py"
        f.write_text(_SRC, encoding="utf-8")
        assert main(["suggest-split", str(f), "--threshold", "0"]) == 0
        assert "component" in capsys.readouterr().out

    def test_under_threshold_no_split(self, tmp_path: Path, capsys) -> None:
        f = tmp_path / "s.py"
        f.write_text(_SRC, encoding="utf-8")
        assert main(["suggest-split", str(f)]) == 0  # ~18 lines < 300
        assert "no split suggested" in capsys.readouterr().out
