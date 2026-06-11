"""v0.1.4: task editing, doc_reading, log, pack, and the `check` project gate."""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import tasks as tk
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestTaskEditing:
    def test_update_and_add_ac(self, proj: Path) -> None:
        tk.add_task("T1.1", "old", 5, ["a"], "pytest")
        tk.update_task("T1.1", title="new", complexity=12)
        tk.add_acceptance("T1.1", "second")
        t = tk.get_task("T1.1")
        assert t["title"] == "new" and t["complexity"] == 12
        assert len(t["acceptance_criteria"]) == 2

    def test_cli_set_and_ac_add(self, proj: Path) -> None:
        tk.add_task("T1.1", "x", 5, ["a"], "pytest")
        assert main(["task", "set", "T1.1", "--complexity", "9"]) == 0
        assert main(["task", "ac-add", "T1.1", "another"]) == 0
        assert tk.get_task("T1.1")["complexity"] == 9
        assert len(tk.get_task("T1.1")["acceptance_criteria"]) == 2


class TestDocReading:
    def test_unread_blocks_then_clears(self, proj: Path) -> None:
        from inertia_forge.doc_reading import collect_doc_reading, mark_read
        findings, _ = collect_doc_reading("investigating", "read_docs", ".", Path("."))
        assert any(f["rule"] == "doc_unread" for f in findings)
        mark_read("investigating")
        findings2, h = collect_doc_reading("investigating", "read_docs", ".", Path("."))
        assert findings2 == [] and h


class TestLogAndPack:
    def test_log_shows_events(self, proj: Path, capsys) -> None:
        from inertia_forge.bypass_prevention import log_behavioral_event
        log_behavioral_event("session_started", "test event")
        assert main(["log"]) == 0
        assert "session_started" in capsys.readouterr().out

    def test_pack_writes_artifact(self, proj: Path) -> None:
        tk.create_plan("feature", "Demo")
        tk.add_task("T1.1", "x", 5, ["a"], "pytest")
        assert main(["pack"]) == 0
        pack = (proj / ".forge" / "context_pack.md").read_text(encoding="utf-8")
        assert "Forge Context Pack" in pack and "T1.1" in pack


class TestCheckGate:
    def test_clean_passes(self, proj: Path) -> None:
        (proj / "ok.py").write_text("x = 1\n", encoding="utf-8")
        assert main(["check", str(proj / "ok.py")]) == 0

    def test_oversized_function_fails(self, proj: Path) -> None:
        body = "\n".join(f"    x{i} = {i}" for i in range(60))
        (proj / "big.py").write_text(f"def huge():\n{body}\n", encoding="utf-8")
        assert main(["check", str(proj / "big.py")]) == 1

    def test_secret_fails(self, proj: Path) -> None:
        (proj / "conf.env").write_text('API_KEY = "supersecret12345"\n', encoding="utf-8")
        assert main(["check", str(proj)]) == 1
