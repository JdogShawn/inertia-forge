"""v0.43.0 — Mermaid export of the deterministic graphs (task DAG + import graph),
renderable by any Mermaid viewer or LLM. Deterministic text output.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import mermaid, tasks as t
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestMermaid:
    def test_nid_sanitizes(self) -> None:
        assert mermaid._nid("T1.2") == "T1_2"
        assert mermaid._nid("a.b-c") == "a_b_c"

    def test_tasks_dag(self, proj: Path) -> None:
        t.add_task("T1.1", "design", 5, ["a"], "pytest")
        t.add_task("T1.2", "build", 3, ["b"], "pytest", depends_on=["T1.1"])
        out = mermaid.tasks_mermaid()
        assert out.startswith("flowchart TD")
        assert "T1_1 --> T1_2" in out          # dependency edge
        assert "classDef ready" in out          # styling present
        assert 'T1_1["T1.1: design"]' in out    # node label

    def test_tasks_done_shaded(self, proj: Path) -> None:
        t.add_task("T1.1", "x", 1, ["a"], "pytest")
        t.start_task("T1.1"); t.check_ac("T1.1", 0); t.complete_task("T1.1")
        assert "class T1_1 done" in mermaid.tasks_mermaid()

    def test_imports_graph(self, tmp_path: Path) -> None:
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        (pkg / "b.py").write_text("from pkg import a\n", encoding="utf-8")
        out = mermaid.imports_mermaid(str(tmp_path))
        assert out.startswith("flowchart LR") and "b --> a" in out

    def test_cli(self, proj: Path) -> None:
        t.add_task("T1.1", "x", 1, ["a"], "pytest")
        assert main(["mermaid", "tasks"]) == 0
        assert main(["mermaid", "imports", "."]) == 0
