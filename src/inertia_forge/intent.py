"""Deterministic intent classification — rule/keyword based, zero LLM.

Maps a free-text request to a plan type (feature/bugfix/refactor/chore) and a
suggested skill, using transparent keyword rules. No model, no guessing you
can't audit — every classification is explainable by the matched keywords.
"""
from __future__ import annotations

import argparse

# (plan_type, suggested_skill, keywords)
_RULES = [
    ("bugfix", "implementing_with_tdd",
     ("fix", "bug", "broken", "error", "crash", "regression", "fails", "failing")),
    ("refactor", "refactoring",
     ("refactor", "clean up", "simplify", "rename", "restructure", "dead code", "tidy")),
    ("chore", "releasing_versions",
     ("release", "version", "bump", "changelog", "docs", "dependency", "ci", "chore")),
    ("feature", "designing_and_implementing",
     ("add", "build", "create", "implement", "new", "feature", "support", "introduce")),
]


def classify(text: str) -> dict:
    """Return {type, skill, matched, confidence} for a request string."""
    low = text.lower()
    best = None
    for ptype, skill, keywords in _RULES:
        hits = [k for k in keywords if k in low]
        if hits and (best is None or len(hits) > len(best["matched"])):
            best = {"type": ptype, "skill": skill, "matched": hits}
    if best is None:
        return {"type": "feature", "skill": "designing_and_implementing",
                "matched": [], "confidence": "low"}
    best["confidence"] = "high" if len(best["matched"]) >= 2 else "medium"
    return best


def run_intent(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="inertia-forge intent")
    parser.add_argument("text", nargs="+", help="the request to classify")
    args = parser.parse_args(argv)
    r = classify(" ".join(args.text))
    print(f"type:       {r['type']}")
    print(f"skill:      {r['skill']}")
    print(f"matched:    {', '.join(r['matched']) or '(none — default)'}")
    print(f"confidence: {r['confidence']}")
    return 0
