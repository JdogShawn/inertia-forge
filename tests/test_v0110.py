"""v0.11.0 — full skill recommender + cross-repo audit (not thin)."""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge.cli import main


class TestRecommender:
    def test_ranks_relevant_skill_top(self) -> None:
        from inertia_forge.recommend import search
        top = search("write a failing test then implement the code")
        assert top and top[0]["skill"] == "implementing_with_tdd"
        assert top[0]["agent"] == "Piston" and "test" in top[0]["matched"]

    def test_review_query(self) -> None:
        from inertia_forge.recommend import search
        skills = [r["skill"] for r in search("review the code change for correctness")]
        assert "reviewing_code" in skills

    def test_searches_doc_text_not_just_name(self) -> None:
        # 'red green refactor' appears in the TDD doc, not the skill name/steps.
        from inertia_forge.recommend import search
        top = search("red green refactor loop")
        assert any(r["skill"] == "implementing_with_tdd" for r in top)

    def test_no_match(self) -> None:
        from inertia_forge.recommend import search
        assert search("zzqqxx nonsensical") == []

    def test_cli(self) -> None:
        assert main(["skills", "search", "implement", "tests"]) == 0


class TestCrossRepoAudit:
    def _mk(self, tmp: Path) -> tuple[Path, Path]:
        cur = tmp / "cur" / "src"
        cur.mkdir(parents=True)
        (cur / "lib.py").write_text(
            "def shared_fn():\n    return 1\n\n\nclass Widget:\n    pass\n", encoding="utf-8")
        sib = tmp / "sibling"
        sib.mkdir(parents=True)
        (sib / "app.py").write_text(
            "from cur.src.lib import shared_fn\nx = shared_fn()\n", encoding="utf-8")
        return cur, sib

    def test_finds_shared_contracts(self, tmp_path: Path) -> None:
        from inertia_forge.audit import audit, exported_symbols
        cur, sib = self._mk(tmp_path)
        assert {"shared_fn", "Widget"} <= exported_symbols(cur)
        result = audit(sib, cur)
        assert "shared_fn" in result["shared"]            # sibling consumes it
        assert "Widget" not in result["shared"]           # sibling doesn't
        assert result["health"]["p0"] == 0

    def test_cli(self, tmp_path: Path, monkeypatch) -> None:
        cur, sib = self._mk(tmp_path)
        monkeypatch.chdir(tmp_path / "cur")
        assert main(["audit", str(sib), "--src", "src"]) == 0

    def test_missing_sibling(self, tmp_path: Path) -> None:
        assert main(["audit", str(tmp_path / "nope")]) == 1
