"""Portable handoff package — move a task's context to another agent.

`handoff pack <task-id>` bundles the task (its description, state, acceptance
criteria), the relevant files (its declared scope plus recently changed files),
agent-specific instructions, and a token estimate into a single `.tgz`
(HANDOFF.md + metadata.json + context/). `handoff unpack <pkg>` extracts it and
returns the metadata. Deterministic — a tarball and JSON, no LLM.

Complements the read-only `handoff` brief: the brief is for *this* repo's next
session; the package is for handing a task to a *different* agent (codex, cursor).
"""
from __future__ import annotations

import json
import subprocess
import tarfile
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path

CHARS_PER_TOKEN = 4

_AGENT_NOTES = {
    "claude": "Use the skills in your agent registry if applicable. Update task status when done.",
    "codex": "Follow AGENTS.md conventions. Use full-auto mode for implementation.",
    "cursor": "Work interactively in the IDE. Reference .cursorrules if present.",
    "generic": "Follow project conventions. Update state when done.",
}


@dataclass
class HandoffPackage:
    task_id: str
    source_agent: str = "claude"
    target_agent: str = "generic"
    token_estimate: int = 0
    files_included: list[str] = field(default_factory=list)
    conversation_summary: str = ""
    task_description: str = ""
    current_state: str = ""
    instructions: str = ""

    def to_metadata(self) -> dict:
        return {
            "task_id": self.task_id, "source_agent": self.source_agent,
            "target_agent": self.target_agent, "token_estimate": self.token_estimate,
            "files_included": self.files_included,
            "conversation_summary": self.conversation_summary,
        }

    def generate_handoff_md(self) -> str:
        lines = [f"# Handoff — {self.task_id}", "",
                 f"**From:** {self.source_agent}  **To:** {self.target_agent}",
                 f"**Token estimate:** {self.token_estimate}", "",
                 "## Task", self.task_description or "(none)", "",
                 "## Current state", self.current_state or "(none)", ""]
        if self.conversation_summary:
            lines += ["## Work so far", self.conversation_summary, ""]
        lines += ["## Instructions", self.instructions or "(none)", "",
                  "## Files", *([f"- {f}" for f in self.files_included] or ["- (none)"])]
        return "\n".join(lines) + "\n"


def _task_info(task: dict | None, task_id: str) -> dict:
    if not task:
        return {"description": f"Task {task_id}", "state": "unknown", "ac": []}
    ac = [c["text"] for c in task.get("acceptance_criteria", [])]
    return {"description": task.get("title", task_id),
            "state": task.get("status", "pending"), "ac": ac}


def _detect_files(task: dict | None, project_root: Path) -> list[Path]:
    found: list[Path] = []
    for rel in (task or {}).get("scope", []) or []:
        p = project_root / rel
        if p.exists() and p not in found:
            found.append(p)
    try:
        r = subprocess.run(["git", "diff", "--name-only", "HEAD~5"],
                           cwd=str(project_root), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", check=False, timeout=10)
        for line in r.stdout.splitlines():
            p = project_root / line.strip()
            if line.strip() and p.exists() and p not in found:
                found.append(p)
    except (OSError, subprocess.SubprocessError):
        pass
    return found[:20]


def _estimate_tokens(files: list[Path]) -> int:
    chars = 0
    for p in files:
        try:
            if p.is_file():
                chars += len(p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            pass
    return chars // CHARS_PER_TOKEN


def _instructions(target_agent: str, info: dict) -> str:
    base = "\n".join(f"- {a}" for a in info["ac"]) or "Complete the task as described."
    return f"{base}\n\n**Agent-specific:** {_AGENT_NOTES.get(target_agent, '')}"


def _write_tarball(pkg: HandoffPackage, files: list[Path], out: Path, root: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out, "w:gz") as tar:
        for name, text in (("HANDOFF.md", pkg.generate_handoff_md()),
                           ("metadata.json", json.dumps(pkg.to_metadata(), indent=2))):
            data = text.encode("utf-8")
            ti = tarfile.TarInfo(name=name)
            ti.size = len(data)
            tar.addfile(ti, BytesIO(data))
        for p in files:
            if p.is_file():
                try:
                    arc = f"context/{p.relative_to(root)}"
                except ValueError:
                    arc = f"context/{p.name}"
                tar.add(p, arcname=arc)


def pack(task_id: str, target_agent: str = "generic", source_agent: str = "claude",
         conversation_summary: str = "", output_path: Path | None = None,
         project_root: Path | None = None) -> Path:
    """Bundle a task's context into a portable `.tgz`. Returns the package path."""
    from inertia_forge import tasks
    root = project_root or Path(".")
    info = _task_info(tasks.get_task(task_id), task_id)
    files = _detect_files(tasks.get_task(task_id), root)
    pkg = HandoffPackage(
        task_id=task_id, source_agent=source_agent, target_agent=target_agent,
        token_estimate=_estimate_tokens(files), files_included=[str(f) for f in files],
        conversation_summary=conversation_summary, task_description=info["description"],
        current_state=info["state"], instructions=_instructions(target_agent, info))
    out = output_path or (root / f"handoff-{task_id}-{target_agent}.tgz")
    _write_tarball(pkg, files, out, root)
    return out


def unpack(package_path: Path, target_dir: Path | None = None) -> dict:
    """Extract a handoff package; returns its metadata dict."""
    dest = target_dir or (Path(".forge") / "incoming")
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(package_path, "r:gz") as tar:
        tar.extractall(dest, filter="data")
    meta = dest / "metadata.json"
    return json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else {}
