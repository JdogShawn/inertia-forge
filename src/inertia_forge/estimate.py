"""Deterministic complexity heuristic.

Estimate a task's complexity from its *shape* — acceptance-criteria count,
verification breadth, and signal words in the title — with a transparent points
formula (no LLM, no calibration server). `task estimate` uses it to pre-fill the
`--complexity` you'd otherwise guess, and `--apply` writes it back.
"""
from __future__ import annotations

# title signal word → added complexity points
_SIGNAL: dict[str, float] = {
    "rewrite": 5, "migrate": 5, "refactor": 3, "integrate": 4, "design": 3,
    "redesign": 4, "port": 3, "optimize": 2, "add": 1, "fix": 1, "remove": 1,
    "rename": 1, "document": 1, "bump": 0.5,
}


def estimate(task: dict) -> float:
    """Points = 1 + 1.5·(AC count) + verification-breadth + title-signal, capped 100."""
    ac = len(task.get("acceptance_criteria", []))
    points = 1 + ac * 1.5
    verify = task.get("verification", "")
    if "&&" in verify or ";" in verify:  # multi-step verification = more surface
        points += 2
    title = task.get("title", "").lower()
    points += max((w for k, w in _SIGNAL.items() if k in title), default=0.0)
    deps = len(task.get("depends_on", []))
    points += deps * 0.5  # integration cost rises with dependencies
    return round(min(points, 100.0), 1)
