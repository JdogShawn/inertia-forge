"""Semantic memory — deterministic vector recall, no model and no server.

Chroma-style abilities (add documents, search by meaning) the INERTIA way: a
local TF-IDF index over your text — knowledge notes, docs, task descriptions —
with cosine ranking. Real ChromaDB needs an embedding *model*; this needs
nothing. The same corpus and query always rank the same way (deterministic),
fully offline. Stored as plain JSONL at ``.forge/semantic.jsonl``.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

STORE = Path(".forge") / "semantic.jsonl"
_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = frozenset((
    "the a an of to in is and or for on with at by it as be this that are was "
    "from but not have has had you your we our they their he she his her its "
    "will can do does did so if then else when which who what how why all any"
).split())


def _tokens(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if len(t) > 2 and t not in _STOP]


def _load() -> list[dict]:
    if not STORE.exists():
        return []
    out = []
    for line in STORE.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def add(text: str, doc_id: str | None = None, meta: dict | None = None) -> str:
    """Add (or upsert) a document. Returns its id."""
    STORE.parent.mkdir(parents=True, exist_ok=True)
    docs = _load()
    doc_id = doc_id or f"d{len(docs) + 1}"
    entry = {"id": doc_id, "text": text, "meta": meta or {}}
    docs = [d for d in docs if d["id"] != doc_id] + [entry]
    STORE.write_text("\n".join(json.dumps(d) for d in docs) + "\n", encoding="utf-8")
    return doc_id


def _idf(docs: list[dict]) -> dict[str, float]:
    n = len(docs)
    df: Counter = Counter()
    for d in docs:
        df.update(set(_tokens(d["text"])))
    return {t: math.log((n + 1) / (df[t] + 1)) + 1 for t in df}


def _vec(tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    tf = Counter(tokens)
    return {t: tf[t] * idf.get(t, 0.0) for t in tf}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    dot = sum(a[t] * b[t] for t in set(a) & set(b))
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def search(query: str, top_k: int = 5) -> list[tuple[float, dict]]:
    """[(score, document)] ranked by TF-IDF cosine similarity to the query."""
    docs = _load()
    if not docs:
        return []
    idf = _idf(docs)
    qv = _vec(_tokens(query), idf)
    scored = [(round(_cosine(qv, _vec(_tokens(d["text"]), idf)), 4), d) for d in docs]
    scored = [(s, d) for s, d in scored if s > 0]
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    return scored[:top_k]


def run_semantic(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge semantic")
    sub = p.add_subparsers(dest="sub", required=True)
    a = sub.add_parser("add", help="index a document")
    a.add_argument("text"); a.add_argument("--id"); a.add_argument("--tag", action="append", default=[])
    s = sub.add_parser("search", help="rank documents by meaning")
    s.add_argument("query"); s.add_argument("--top", type=int, default=5)
    sub.add_parser("list", help="list indexed documents")
    sub.add_parser("index-learn", help="import the knowledge ledger into the index")
    args = p.parse_args(argv)

    if args.sub == "add":
        print(f"{seal('ok')} indexed {add(args.text, args.id, {'tags': args.tag})}")
        return 0
    if args.sub == "list":
        for d in _load():
            print(f"  {d['id']:10} {d['text'][:68]}")
        return 0
    if args.sub == "index-learn":
        from inertia_forge.learn import all_entries
        entries = all_entries()
        for i, e in enumerate(entries, 1):
            add(e.get("text", ""), f"learn{i}", {"tags": e.get("tags", [])})
        print(f"{seal('ok')} indexed {len(entries)} knowledge entr(y/ies)")
        return 0
    results = search(args.query, args.top)
    if not results:
        print("(no matches)")
        return 0
    for score, d in results:
        print(f"  {paint(f'{score:.3f}', 'accent')}  {paint(d['id'], 'muted')}  {d['text'][:64]}")
    return 0
