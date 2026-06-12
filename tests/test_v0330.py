"""v0.33.0 — module split adviser (suggest-split). Deterministic AST clustering.
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
    def test_clusters_by_prefix(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text(_SRC, encoding="utf-8")
        sugg = splitter.suggest(f)
        labels = {s[0] for s in sugg}
        assert "check" in labels and "run" in labels
        check = next(s for s in sugg if s[0] == "check")
        assert len(check[1]) == 4 and check[2] > 0  # 4 functions, some lines

    def test_small_file_no_suggestion(self, tmp_path: Path) -> None:
        f = tmp_path / "s.py"
        f.write_text("def a():\n    pass\ndef b():\n    pass\n", encoding="utf-8")
        assert splitter.suggest(f) == []

    def test_no_cluster_when_unique_prefixes(self, tmp_path: Path) -> None:
        src = "\n".join(f"def uniq{i}(x):\n    return x\n" for i in range(10))
        f = tmp_path / "u.py"
        f.write_text(src, encoding="utf-8")
        assert splitter.suggest(f) == []  # each prefix unique → no group of 3

    def test_prefix_and_dest(self) -> None:
        assert splitter._prefix("check_env") == "check"
        assert splitter._prefix("_cmd_run") == "_cmd"
        assert splitter._prefix("run") == "run"
        assert splitter._dest_module("m", "_check") == "m_checks.py"
        assert splitter._dest_module("m", "run") == "m_commands.py"


class TestCli:
    def test_advisory_exit_0(self, tmp_path: Path, capsys) -> None:
        f = tmp_path / "m.py"
        f.write_text(_SRC, encoding="utf-8")
        assert main(["suggest-split", str(f)]) == 0
        assert "extraction candidate" in capsys.readouterr().out

    def test_clean_file(self, tmp_path: Path, capsys) -> None:
        f = tmp_path / "s.py"
        f.write_text("def a():\n    pass\n", encoding="utf-8")
        assert main(["suggest-split", str(f)]) == 0
        assert "no split suggested" in capsys.readouterr().out
