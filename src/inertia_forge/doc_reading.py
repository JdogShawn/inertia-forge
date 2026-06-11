"""`doc_reading` evidence + the `inertia-forge read` marker.

Gate a skill's phase on "the methodology doc was actually read." A skill may
declare ``doc: path/to/ref.md`` in its definition; ``inertia-forge read <skill>``
records that you've read it (verifying the file exists), and the doc_reading
verifier keeps the gate open until that marker is present.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DOCS_READ = Path(".forge") / "docs_read.json"


def _load() -> list[str]:
    if not DOCS_READ.exists():
        return []
    try:
        data = json.loads(DOCS_READ.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def mark_read(skill: str) -> None:
    skill = skill.replace("-", "_")
    data = _load()
    if skill not in data:
        data.append(skill)
        DOCS_READ.parent.mkdir(parents=True, exist_ok=True)
        DOCS_READ.write_text(json.dumps(sorted(data), indent=2) + "\n", encoding="utf-8")


def is_read(skill: str) -> bool:
    return skill.replace("-", "_") in _load()


def _stamp(skill: str, phase: str, target: str) -> str:
    ts = datetime.now(timezone.utc).isoformat()
    return hashlib.sha256(
        f"{skill}|{phase}|{target}|{ts}|doc_reading".encode()
    ).hexdigest()


def collect_doc_reading(
    skill: str, phase: str, target: str, analysis_dir,
) -> tuple[list[dict], str]:
    """doc_reading mode — P0 until the skill's methodology doc is marked read
    (and, if the skill declares a `doc:` path, until that file exists)."""
    from inertia_forge.skill_registry import get_skill

    findings: list[dict] = []
    try:
        doc = get_skill(skill).doc
    except (ValueError, AttributeError):
        doc = ""
    if doc and not Path(doc).is_file():
        findings.append({"severity": "P0", "rule": "doc_missing", "file": doc,
                         "line": 0, "message": f"doc_reading: declared doc {doc!r} not found"})
    if not is_read(skill):
        findings.append({"severity": "P0", "rule": "doc_unread", "file": "<docs>",
                         "line": 0, "message": f"doc_reading: read the methodology first — "
                                               f"`inertia-forge read {skill}`"})
    return findings, _stamp(skill, phase, target)
