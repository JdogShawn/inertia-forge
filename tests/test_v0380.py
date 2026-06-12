"""v0.38.0 — Sherlock-driven: unified `scan` battery, MCP gap closed, review
self-flag fixed (console.log/debugger are JS-only, not Python).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import review, scan
from inertia_forge.cli import main
from inertia_forge.mcp import handle


class TestScan:
    def test_clean_tree_passes(self, tmp_path: Path, monkeypatch) -> None:
        (tmp_path / "m.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert main(["scan", "."]) == 0

    def test_gating_failure_fails(self, tmp_path: Path, monkeypatch) -> None:
        (tmp_path / "m.py").write_text("def f():\n    eval('x')\n", encoding="utf-8")  # vet P1
        monkeypatch.chdir(tmp_path)
        assert main(["scan", "."]) == 1

    def test_battery_runs_all_analyzers(self, tmp_path: Path, monkeypatch) -> None:
        (tmp_path / "m.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        results = scan.battery(".")
        assert len(results) == 8
        assert results[0][0] == "arch" and any("xref" in lbl for lbl, _, _ in results)


class TestMcpGapClosed:
    def test_new_analysis_tools_exposed(self) -> None:
        resp = handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        names = {t["name"] for t in resp["result"]["tools"]}
        assert {"forge_scan", "forge_xref", "forge_consistency", "forge_preflight",
                "forge_coverage", "forge_query", "forge_semantic_search"} <= names

    def test_tool_count_grew(self) -> None:
        from inertia_forge.mcp import _TOOLS
        assert len(_TOOLS) >= 28


class TestReviewSelfFlagFixed:
    def test_console_log_in_python_string_not_flagged(self, tmp_path: Path) -> None:
        (tmp_path / "m.py").write_text('msg = "use console.log to debug"  # debugger note\n',
                                       encoding="utf-8")
        # JS-isms in a Python string/comment are no longer P1
        assert all(f["severity"] != "P1" for f in review.review_file(tmp_path / "m.py"))

    def test_console_log_still_flagged_in_js(self, tmp_path: Path) -> None:
        (tmp_path / "x.js").write_text("console.log('x')\n", encoding="utf-8")
        assert any(f["severity"] == "P1" for f in review.review_file(tmp_path / "x.js"))

    def test_real_python_debug_still_flagged(self, tmp_path: Path) -> None:
        (tmp_path / "b.py").write_text("def f():\n    breakpoint()\n", encoding="utf-8")
        assert any(f["severity"] == "P1" for f in review.review_file(tmp_path / "b.py"))
