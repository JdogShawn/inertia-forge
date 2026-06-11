"""Context cache — store/retrieve content blobs by key. Deterministic, zero LLM.

Caches large context (pack output, analysis dumps, prompts) under
`.forge/cache/<key>` so it can be reused across sessions without recomputing.
Keys are sanitized to a safe filename; `set` reads a file or stdin, `get`
writes to stdout.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

CACHE_DIR = Path(".forge") / "cache"


def _key_path(key: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", key)
    return CACHE_DIR / safe


def set_blob(key: str, content: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _key_path(key)
    path.write_text(content, encoding="utf-8")
    return path


def get_blob(key: str) -> str | None:
    path = _key_path(key)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def has(key: str) -> bool:
    return _key_path(key).exists()


def keys() -> list[str]:
    if not CACHE_DIR.exists():
        return []
    return sorted(p.name for p in CACHE_DIR.iterdir() if p.is_file())


def run_cache(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge cache")
    sub = p.add_subparsers(dest="sub", required=True)
    s = sub.add_parser("set"); s.add_argument("key"); s.add_argument("file", nargs="?", default="-")
    g = sub.add_parser("get"); g.add_argument("key")
    sub.add_parser("list")
    r = sub.add_parser("rm"); r.add_argument("key")
    sub.add_parser("clear")
    args = p.parse_args(argv)

    if args.sub == "set":
        content = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
        path = set_blob(args.key, content)
        print(f"cached {args.key} ({len(content)} bytes) -> {path}")
        return 0
    if args.sub == "get":
        blob = get_blob(args.key)
        if blob is None:
            print(f"cache miss: {args.key}", file=sys.stderr)
            return 1
        sys.stdout.write(blob)
        return 0
    if args.sub == "rm":
        path = _key_path(args.key)
        if path.exists():
            path.unlink()
            print(f"removed {args.key}")
            return 0
        print(f"no such key: {args.key}")
        return 1
    if args.sub == "clear":
        n = 0
        for k in keys():
            (CACHE_DIR / k).unlink()
            n += 1
        print(f"cleared {n} entr(y/ies)")
        return 0
    ks = keys()
    if not ks:
        print("(cache empty)")
        return 0
    for k in ks:
        path = CACHE_DIR / k
        age = int(time.time() - path.stat().st_mtime)
        print(f"  {k:28} {path.stat().st_size:>8} B   {age}s ago")
    return 0
