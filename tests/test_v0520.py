"""v0.52.0 — portable handoff package (pack/unpack a task's context as a .tgz).
Deterministic: tarball + JSON, no LLM.
"""
from __future__ import annotations

import tarfile
from pathlib import Path

import pytest

from inertia_forge import tasks
from inertia_forge.cli import main
from inertia_forge.handoff_pack import HandoffPackage, pack, unpack


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


def _task(tid: str, scope: list[str] | None = None) -> None:
    tasks.add_task(tid, f"task {tid}", 10, ["it works"], "pytest -q")
    if scope:
        tasks.update_task(tid, scope=scope)


class TestPackage:
    def test_metadata_and_md(self) -> None:
        pkg = HandoffPackage(task_id="T1.1", target_agent="codex", token_estimate=42,
                             files_included=["a.py"], task_description="do x")
        assert pkg.to_metadata()["task_id"] == "T1.1"
        md = pkg.generate_handoff_md()
        assert "T1.1" in md and "codex" in md and "do x" in md and "a.py" in md


class TestPackUnpack:
    def test_pack_creates_tgz(self, proj: Path) -> None:
        (proj / "w.py").write_text("x = 1\n", encoding="utf-8")
        _task("T1.1", scope=["w.py"])
        out = pack("T1.1", target_agent="codex", project_root=proj)
        assert out.exists() and out.suffix == ".tgz"
        with tarfile.open(out, "r:gz") as tar:
            names = tar.getnames()
        assert "HANDOFF.md" in names and "metadata.json" in names
        assert any(n.startswith("context/") and n.endswith("w.py") for n in names)

    def test_roundtrip(self, proj: Path) -> None:
        _task("T2.1")
        out = pack("T2.1", source_agent="claude", target_agent="cursor", project_root=proj)
        meta = unpack(out, target_dir=proj / "incoming")
        assert meta["task_id"] == "T2.1" and meta["source_agent"] == "claude"
        assert (proj / "incoming" / "HANDOFF.md").exists()

    def test_unknown_task_still_packs(self, proj: Path) -> None:
        out = pack("T9.9", project_root=proj)  # no such task → minimal package
        assert out.exists()


class TestCli:
    def test_cli_pack_unpack(self, proj: Path) -> None:
        _task("T1.1")
        assert main(["handoff", "pack", "T1.1", "--to", "codex"]) == 0
        pkg = next(proj.glob("handoff-T1.1-*.tgz"))
        assert main(["handoff", "unpack", str(pkg)]) == 0

    def test_bare_handoff_still_brief(self, proj: Path) -> None:
        _task("T1.1")
        assert main(["handoff"]) == 0  # the read-only continuity brief
