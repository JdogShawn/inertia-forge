"""Deterministic skill + agent recommender — full-text search over the corpus.

Given a request, rank the skills by relevance across three weighted fields:
the skill name (×5), its step names (×2), and its full methodology doc (×1) —
then map each to the agent that runs it. No model: every score is a transparent
keyword tally you can reproduce.
"""
from __future__ import annotations

import argparse
import re

_STOP = {"the", "a", "an", "to", "of", "and", "or", "for", "with", "in", "on",
         "is", "it", "this", "that", "my", "we", "i", "be", "do", "how"}

_SKILL_AGENT = {
    "implementing_with_tdd": "Piston", "designing_and_implementing": "Vector",
    "reviewing_code": "Caliper", "refactoring": "Piston",
    "releasing_versions": "Bastion", "security_audit": "Sentinel",
    "investigating": "Caliper", "finishing_branches": "Bastion",
}


def _doc_text(name: str) -> str:
    from inertia_forge import assets
    p = assets.SKILLS / name.replace("_", "-") / "SKILL.md"
    try:
        return p.read_text(encoding="utf-8").lower() if p.exists() else ""
    except OSError:
        return ""


def _tokens(query: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", query.lower())
            if w not in _STOP and len(w) > 2]


def search(query: str, top: int = 5) -> list[dict]:
    from inertia_forge.skill_registry import get_all_skills

    toks = _tokens(query)
    results = []
    for name, sk in get_all_skills().items():
        nm = name.lower().replace("_", " ")
        steps = " ".join(sk.steps).lower().replace("_", " ")
        doc = _doc_text(name)
        score, matched = 0, set()
        for t in toks:
            hits = nm.count(t) * 5 + steps.count(t) * 2 + doc.count(t)
            if hits:
                matched.add(t)
            score += hits
        if score:
            results.append({"skill": name, "score": score,
                            "matched": sorted(matched),
                            "agent": _SKILL_AGENT.get(name, "Piston")})
    results.sort(key=lambda r: (-r["score"], r["skill"]))
    return results[:top]


def run_search(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge skills search")
    p.add_argument("query", nargs="+")
    args = p.parse_args(argv)
    hits = search(" ".join(args.query))
    if not hits:
        print("(no matching skill)")
        return 1
    for r in hits:
        print(f"  {r['skill']:28} score={r['score']:>3}  agent={r['agent']:8}  "
              f"[{', '.join(r['matched'])}]")
    return 0
