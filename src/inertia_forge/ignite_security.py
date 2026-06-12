"""Pre-finalize security gate — Bastion audits the branch diff and can BLOCK.

Fetch the full branch diff, hand it to the security-gate agent (Bastion, from the
bundled roster), and BLOCK if it returns a P0 finding. Fail-closed — if the agent
errors, the gate blocks (safer to stop than to ship an unaudited change). The
diff goes through a temp file so a large sprint diff never hits the CLI
argument-length limit (Windows ~32 KB).
"""
from __future__ import annotations

import re
import tempfile
from pathlib import Path

from inertia_forge.review_agents import _DATA_END, _DATA_FENCE

_AUDIT = (
    "Audit this branch diff for security vulnerabilities, credential/secret "
    "exposure, injection, unsafe deserialization, and OWASP issues. Classify "
    "each finding with a markdown header — ### P0 (must block), ### P1, or ### P2."
)


def branch_diff(root: Path, base: str = "main") -> str:
    """The full branch diff against *base* (`git diff base...HEAD`)."""
    from inertia_forge.gitcheck import _git
    return _git(root, "diff", f"{base}...HEAD")


def _dispatch_bastion(diff: str, cli: str, model: str | None, root: Path) -> str | None:
    """Audit a (possibly large) diff via a temp file the agent reads."""
    tf = tempfile.NamedTemporaryFile("w", suffix=".diff", prefix="forge_sec_",
                                     delete=False, encoding="utf-8")
    try:
        tf.write(diff)
        tf.close()
        from inertia_forge.invoker import dispatch
        context = (f"{_AUDIT}\n\nThe diff to audit is written at: {tf.name}\n"
                   "Use the Read tool to read that file, then audit its contents.")
        resp = dispatch("bastion", context, cli=cli, model=model, working_dir=root)
        return None if resp.is_error else resp.result
    finally:
        Path(tf.name).unlink(missing_ok=True)


def security_gate(root: Path, base: str = "main", cli: str = "claude",
                  model: str | None = None, dispatcher=None) -> dict:
    """Audit the branch diff. {blocked, action, findings}; P0 or error → blocked."""
    diff = branch_diff(root, base)
    if not diff.strip():
        return {"blocked": False, "action": "skipped", "findings": ""}
    if dispatcher is not None:
        text = dispatcher(_AUDIT + _DATA_FENCE + diff + _DATA_END)
    else:
        text = _dispatch_bastion(diff, cli, model, root)
    if text is None:
        return {"blocked": True, "action": "error", "findings": ""}  # fail-closed
    blocked = bool(re.search(r"###?\s*P0", text, re.IGNORECASE))
    return {"blocked": blocked,
            "action": "request_changes" if blocked else "approve",
            "findings": text}
