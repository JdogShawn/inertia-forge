"""v0.32.0 — deterministic semantic memory (chroma-style recall, no model).
Local TF-IDF cosine index; same corpus + query always ranks the same.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import semantic
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestIndex:
    def test_tokens_drop_stopwords_and_short(self) -> None:
        toks = semantic._tokens("the quick brown fox is a")
        assert "quick" in toks and "the" not in toks and "is" not in toks

    def test_add_and_load(self, proj: Path) -> None:
        semantic.add("hello world", "a", {"tags": ["x"]})
        docs = semantic._load()
        assert len(docs) == 1 and docs[0]["id"] == "a" and docs[0]["meta"]["tags"] == ["x"]

    def test_upsert_same_id(self, proj: Path) -> None:
        semantic.add("first", "k")
        semantic.add("second", "k")
        docs = [d for d in semantic._load() if d["id"] == "k"]
        assert len(docs) == 1 and docs[0]["text"] == "second"

    def test_cosine_bounds(self) -> None:
        assert semantic._cosine({"a": 1.0}, {"a": 1.0}) == 1.0
        assert semantic._cosine({"a": 1.0}, {"b": 1.0}) == 0.0


class TestSearch:
    def test_ranks_relevant_first(self, proj: Path) -> None:
        semantic.add("task dependency graph computes blocked tasks", "deps")
        semantic.add("secret scanning finds api keys and tokens", "sec")
        top = semantic.search("blocked dependency tasks")
        assert top[0][1]["id"] == "deps" and top[0][0] > 0

    def test_deterministic(self, proj: Path) -> None:
        semantic.add("alpha beta gamma", "x")
        semantic.add("beta gamma delta", "y")
        assert semantic.search("beta gamma") == semantic.search("beta gamma")

    def test_no_match_empty(self, proj: Path) -> None:
        semantic.add("completely unrelated content", "a")
        assert semantic.search("zzqqxx nonexistent") == []

    def test_empty_index(self, proj: Path) -> None:
        assert semantic.search("anything") == []


class TestCli:
    def test_add_search_list(self, proj: Path, capsys) -> None:
        assert main(["semantic", "add", "forge gates skills deterministically", "--id", "g"]) == 0
        assert main(["semantic", "list"]) == 0
        assert main(["semantic", "search", "gates"]) == 0
        assert "forge gates" in capsys.readouterr().out

    def test_index_learn(self, proj: Path) -> None:
        main(["learn", "add", "run vet before shipping a release"])
        assert main(["semantic", "index-learn"]) == 0
        assert semantic.search("vet release") and semantic.search("vet release")[0][0] > 0
