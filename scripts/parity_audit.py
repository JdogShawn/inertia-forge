#!/usr/bin/env python3
"""Parity auditor — does our port preserve a reference module's *behavior*?

Names differ between a reference implementation and an inertia-native port, so
this tool ignores names and compares the behavior-defining, naming-independent
signals a faithful port of an intelligent system must preserve. For every signal
it records the exact SOURCE POINTER (``file:line``) so you can jump straight to
the missing code and read the full segment.

Signal categories (think: what makes the behavior, not the names):
  • size           code LOC — a 300→80 line drop is a downscope red flag
  • command        subprocess argv (git/gh/agent CLI) — what it does to the system
  • threshold      numeric limits/ratios/timeouts/caps — the tuning
  • status         severity/action/status string tokens (P0, request_changes, …)
  • rule           regex patterns (validation, parsing, sanitization)
  • prompt         long string literals (agent instructions)
  • model          dataclass field-sets and enum members
  • telemetry      signal/event emission — emit/record + signal_type event names
  • dispatch       agent/LLM invocation points (the intelligence touchpoints)
  • exception      custom error classes (defined or raised)
  • concurrency    ThreadPool / async / parallel execution
  • decision       per-function branch density (collapsed case-handling = downscope)
  • safety         encoding (errors=…), fail-closed, data-fencing, traversal guards
  • config         snake_case config keys

Each missing signal is reported with its source ``file:line`` pointer. A JSON
progress state persists resolved gaps so re-runs show what's left.

    python parity_audit.py <ref_module.py|dir> <port.py|dir> [--out report.md] [--state s.json]

Universal — point it at any reference module and any port. Stdlib only. Heuristic:
each item is a candidate to verify, not a verdict.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path

_TRIVIAL_NUMS = {0, 1, 2, -1, 100, 10, 3, 4, 5}
_EXTERNAL_BINS = {"git", "gh", "claude", "codex", "gemini", "ollama", "npm", "pip",
                  "docker", "kubectl", "bash", "sh", "pytest"}
_STATUS_HINT = re.compile(r"^(P[0-9]|done|pending|blocked|failed|approve|comment|"
                          r"request_changes|readonly|readwrite|skipped|success|"
                          r"hook_failed|in_progress|partial|error|warn|critical|high|info|"
                          r"plan|auto|full|bypassPermissions)$")
_CONFIG_KEY = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$")
_EVENT_NAME = re.compile(r"^[a-z][a-z0-9_]+$")
_DISPATCH_NAMES = ("HeadlessSession", "AgentInvoker", "AgentSession", "SecurityAgent",
                   "PlannerAgent", "ReviewerAgent")
_SAFETY_MARKERS = ("backslashreplace", "errors=", "DATA START", "DATA END",
                   "--output-format", "fail-closed", "fail_closed", "..", "permission")


@dataclass
class Sig:
    cat: str
    key: str        # normalized comparison key
    label: str      # human display
    line: int


# ── extraction ────────────────────────────────────────────────────────────────
def _s(node: ast.AST) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _command(node: ast.AST) -> str | None:
    if not isinstance(node, ast.List) or not node.elts:
        return None
    head = _s(node.elts[0])
    if head not in _EXTERNAL_BINS:
        return None
    toks = [head]
    for el in node.elts[1:3]:
        s = _s(el)
        if s and not s.startswith("-"):
            toks.append(s)
        else:
            break
    return " ".join(toks)


def _branch_count(fn: ast.AST) -> int:
    return sum(isinstance(n, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.match_case))
              for n in ast.walk(fn))


def extract(text: str) -> list[Sig]:
    sigs: list[Sig] = []
    tree = ast.parse(text)

    def add(cat: str, key: str, label: str, line: int) -> None:
        sigs.append(Sig(cat, key, label, line))

    for node in ast.walk(tree):
        ln = getattr(node, "lineno", 0)
        if cmd := _command(node):
            add("command", f"cmd:{cmd}", cmd, ln)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
                and not isinstance(node.value, bool):
            v = node.value
            if abs(v) not in _TRIVIAL_NUMS and v not in _TRIVIAL_NUMS:
                lit = str(int(v)) if v == int(v) else str(v)
                add("threshold", f"num:{lit}", lit, ln)
        if (s := _s(node)) is not None:
            if _STATUS_HINT.match(s):
                add("status", f"st:{s}", s, ln)
            if len(s) >= 60:
                add("prompt", f"pr:{_fingerprint(s)}", _fingerprint(s), ln)
            if _CONFIG_KEY.match(s):
                add("config", f"cfg:{s}", s, ln)
            for m in _SAFETY_MARKERS:
                if m in s:
                    add("safety", f"safe:{m}", m, ln)
        if isinstance(node, ast.Call):
            _extract_call(node, ln, add)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            bc = _branch_count(node)
            if bc >= 5:
                add("decision", f"dec:{node.name}", f"{node.name} ({bc} branches)", ln)
            if isinstance(node, ast.AsyncFunctionDef):
                add("concurrency", "conc:async", f"async {node.name}", ln)
        if isinstance(node, ast.ClassDef):
            _extract_class(node, ln, add)
        if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call) \
                and isinstance(node.exc.func, ast.Name) and node.exc.func.id.endswith(("Error", "Exception")):
            add("exception", f"exc:{node.exc.func.id}", f"raise {node.exc.func.id}", ln)
        if isinstance(node, ast.Name) and node.id in ("ThreadPoolExecutor", "as_completed"):
            add("concurrency", f"conc:{node.id}", node.id, ln)
    return sigs


def _extract_call(node: ast.Call, ln: int, add) -> None:
    fn = node.func
    # regex rules
    if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) and fn.value.id == "re" \
            and node.args and (p := _s(node.args[0])):
        add("rule", f"rx:{_rx_core(p)}", p[:48], ln)
    # config .get("key")
    if isinstance(fn, ast.Attribute) and fn.attr == "get" and node.args and (k := _s(node.args[0])) \
            and _CONFIG_KEY.match(k):
        add("config", f"cfg:{k}", k, ln)
    # telemetry: *.record( / emit_*( / *.append( a signal
    name = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
    if name == "record" or name.startswith("emit"):
        add("telemetry", f"tel:{name}", f"{name}()", ln)
    # dispatch / intelligence touchpoints
    if isinstance(fn, ast.Name) and fn.id in _DISPATCH_NAMES:
        add("dispatch", f"disp:{fn.id}", fn.id, ln)
    if isinstance(fn, ast.Attribute) and fn.attr in ("invoke", "continue_session", "dispatch"):
        add("dispatch", f"disp:{fn.attr}", f".{fn.attr}()", ln)


def _extract_class(node: ast.ClassDef, ln: int, add) -> None:
    bases = {b.id for b in node.bases if isinstance(b, ast.Name)}
    bases |= {b.attr for b in node.bases if isinstance(b, ast.Attribute)}
    if any(b.endswith(("Error", "Exception")) for b in bases):
        add("exception", f"exc:{node.name}", f"class {node.name}", ln)
    is_enum = "Enum" in bases
    is_dc = any((isinstance(d, ast.Name) and d.id == "dataclass") or
                (isinstance(d, ast.Attribute) and d.attr == "dataclass")
                for d in node.decorator_list)
    if not (is_enum or is_dc):
        return
    fields: set[str] = set()
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            fields.add(stmt.target.id)
        elif isinstance(stmt, ast.Assign):
            fields |= {t.id for t in stmt.targets if isinstance(t, ast.Name)}
    key = "model:" + ",".join(sorted(fields))
    add("model", key, f"{node.name}{{{', '.join(sorted(fields))}}}", ln)


def _fingerprint(s: str) -> str:
    return " ".join(re.findall(r"[A-Za-z]{3,}", s)[:6]).lower()


def _rx_core(p: str) -> str:
    return re.sub(r"\\s|\\b|[()?:]", "", p)[:14]


# ── checking ──────────────────────────────────────────────────────────────────
def _loc(text: str) -> int:
    return sum(1 for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#"))


def _present(sig: Sig, target: str, target_keys: set[str]) -> bool:
    if sig.cat == "command":
        bin_, _, sub = sig.label.partition(" ")
        return f"{bin_} {sub}".strip() in target or (f'"{bin_}"' in target and (not sub or f'"{sub}"' in target))
    if sig.cat == "threshold":
        return bool(re.search(rf"(?<![\d.]){re.escape(sig.label)}(?![\d.])", target))
    if sig.cat == "status":
        return sig.label in target
    if sig.cat == "rule":
        core = _rx_core(sig.key[3:])
        return len(core) >= 4 and core in re.sub(r"\\s|\\b", "", target)
    if sig.cat == "prompt":
        return all(w in target.lower() for w in sig.label.split()[:3])
    if sig.cat == "config":
        return sig.label in target
    if sig.cat == "safety":
        return sig.label in target
    if sig.cat == "model":
        return sig.key in target_keys
    if sig.cat in ("telemetry", "dispatch", "concurrency", "exception"):
        return sig.key in target_keys
    if sig.cat == "decision":
        return True  # informational — size signal, judged via LOC
    return sig.key in target_keys


def _signal_keys(sigs: list[Sig]) -> set[str]:
    return {s.key for s in sigs}


def _best_match(src: list[Sig], files: list[tuple]) -> tuple:
    src_keys = _signal_keys(src)
    best = (None, 0, 0)
    for path, text, sigs in files:
        overlap = len(src_keys & _signal_keys(sigs))
        if overlap > best[2]:
            best = (path, _loc(text), overlap)
    return best


def audit_module(src_path: Path, target_text: str, files: list[tuple]) -> dict:
    text = src_path.read_text(encoding="utf-8")
    src = extract(text)
    tkeys: set[str] = set()
    for _, _, sigs in files:
        tkeys |= _signal_keys(sigs)
    miss = [s for s in src if not _present(s, target_text, tkeys)]
    match_path, match_loc, overlap = _best_match(src, files)
    cats: dict[str, list[int]] = {}
    for s in src:
        c = cats.setdefault(s.cat, [0, 0]); c[1] += 1
    for s in src:
        if _present(s, target_text, tkeys):
            cats[s.cat][0] += 1
    return {"module": src_path.name, "path": str(src_path), "src_loc": _loc(text),
            "match": (match_path.name if match_path else None), "match_loc": match_loc,
            "overlap": overlap, "missing": miss, "cats": cats, "n": len(src)}


# ── reporting ─────────────────────────────────────────────────────────────────
def _loc_flag(src_loc: int, match_loc: int) -> str:
    if not match_loc:
        return "⚠ NO MATCH (likely not ported)"
    ratio = src_loc / match_loc
    if ratio >= 1.8:
        return f"⚠ DOWNSCOPE? source {src_loc}L vs port {match_loc}L ({ratio:.1f}×)"
    return f"source {src_loc}L vs port {match_loc}L"


def render(res: dict, done: set[str]) -> str:
    ok = sum(c[0] for c in res["cats"].values())
    pct = round(100 * ok / res["n"]) if res["n"] else 100
    lines = [f"## {res['module']}  ({pct}% · {ok}/{res['n']} signals)",
             f"_{_loc_flag(res['src_loc'], res['match_loc'])}"
             f"{' · best match: ' + res['match'] if res['match'] else ''}_", ""]
    by_cat = ", ".join(f"{c} {v[0]}/{v[1]}" for c, v in sorted(res["cats"].items()))
    lines.append(f"`{by_cat}`\n")
    missing = [m for m in res["missing"] if f"{res['path']}:{m.line}" not in done]
    if not missing:
        lines.append("### ✓ no unresolved behavioral gaps")
        return "\n".join(lines)
    lines.append("### ⚠ gaps — read the source then implement")
    for m in sorted(missing, key=lambda s: (s.cat, s.line)):
        lines.append(f"  - [ ] **{m.cat}** `{m.label}`  → `{res['path']}:{m.line}`")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="behavioral parity auditor (port vs reference)")
    p.add_argument("source")
    p.add_argument("target")
    p.add_argument("--glob", default="*.py")
    p.add_argument("--out", default=None)
    p.add_argument("--state", default=None, help="JSON file of resolved 'path:line' pointers")
    args = p.parse_args(argv)

    target_text, _, files = _read_target(Path(args.target))
    done: set[str] = set()
    if args.state and Path(args.state).exists():
        done = set(json.loads(Path(args.state).read_text(encoding="utf-8")).get("resolved", []))

    src_path = Path(args.source)
    sources = [src_path] if src_path.is_file() else sorted(src_path.glob(args.glob))
    results = [audit_module(s, target_text, files) for s in sources
               if s.suffix == ".py" and not _skip(s)]

    g_ok = sum(sum(c[0] for c in r["cats"].values()) for r in results)
    g_n = sum(r["n"] for r in results)
    g_pct = round(100 * g_ok / g_n) if g_n else 100
    flags = [r["module"] for r in results if r["match_loc"] and r["src_loc"] / r["match_loc"] >= 1.8]
    header = (f"# Parity audit — {args.source} → {args.target}\n\n"
              f"**Behavioral coverage: {g_ok}/{g_n} ({g_pct}%)** across {len(results)} module(s)\n\n"
              f"{'⚠ downscope red flags: ' + ', '.join(flags) if flags else 'no LOC red flags'}\n\n"
              "Heuristic — each item is a candidate to verify. Pointers are `file:line` "
              "in the reference; open them to read the full missing segment.\n")
    out = header + "\n\n".join(render(r, done) for r in results) + "\n"
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"wrote {args.out} — {g_pct}% coverage, {len(flags)} LOC red flag(s)")
    else:
        print(out)
    return 0


def _skip(path: Path) -> bool:
    return path.name == "__init__.py" or "__pycache__" in path.parts


def _read_target(path: Path) -> tuple[str, list, list[tuple]]:
    paths = [path] if path.is_file() else sorted(path.rglob("*.py"))
    texts, triples = [], []
    for f in paths:
        if _skip(f):
            continue
        try:
            txt = f.read_text(encoding="utf-8")
            sigs = extract(txt)
        except (OSError, SyntaxError):
            continue
        texts.append(txt)
        triples.append((f, txt, sigs))
    return "\n".join(texts), [], triples


if __name__ == "__main__":
    raise SystemExit(main())
