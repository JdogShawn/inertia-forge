"""INERTIA forge — composite output kit.

Rules, panels, key/value blocks, orbital progress, and branded status lines
(`ok`/`warn`/`err`/`info`). Commands compose their output from these so the
whole forge looks like one instrument. Every renderer degrades to clean ASCII
under NO_COLOR or a narrow encoding.
"""
from __future__ import annotations

import shutil
import sys
from typing import Iterable, Sequence, Tuple

from inertia_forge.glyphs import g, seal
from inertia_forge.palette import paint, strip_ansi


def _term_width(width: int = 0) -> int:
    return width or min(shutil.get_terminal_size((80, 24)).columns, 80)


def _encodable(s: str) -> bool:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        s.encode(enc)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def rule(label: str = "", width: int = 0, role: str = "border") -> str:
    """A horizontal rule, optionally with a centred label."""
    width = _term_width(width)
    dash = "─" if _encodable("─") else "-"
    if not label:
        return paint(dash * width, role)
    pad = width - len(label) - 2
    left = pad // 2
    return (paint(dash * left, role) + " " + paint(label, "title", bold=True)
            + " " + paint(dash * (pad - left), role))


def heading(text: str, width: int = 0) -> str:
    """A section heading: the title over a brand rule."""
    mark = paint(g("spark"), "accent")
    return f"{mark} {paint(text, 'title', bold=True)}\n{rule(width=width)}"


def panel(body: str, title: str = "", width: int = 0, role: str = "frame") -> str:
    """Frame *body* in a rounded box with an optional title in the top edge."""
    rounded = _encodable("╭─│")
    tl, tr, bl, br, h, v = (("╭", "╮", "╰", "╯", "─", "│")
                            if rounded else ("+", "+", "+", "+", "-", "|"))
    lines = body.split("\n")
    inner = max([len(strip_ansi(x)) for x in lines] + [len(strip_ansi(title)) + 2])
    inner = min(inner, _term_width(width) - 2)
    top = f"{tl}{h} {paint(title, 'title', bold=True)} {h * (inner - len(strip_ansi(title)) - 3)}{tr}" \
        if title else f"{tl}{h * inner}{tr}"
    out = [paint(top, role)]
    for ln in lines:
        gap = inner - len(strip_ansi(ln))
        out.append(paint(v, role) + ln + " " * max(0, gap) + paint(v, role))
    out.append(paint(f"{bl}{h * inner}{br}", role))
    return "\n".join(out)


def kv(pairs: Sequence[Tuple[str, str]], role: str = "muted") -> str:
    """Aligned ``key : value`` block; keys painted muted, values plain."""
    if not pairs:
        return ""
    klen = max(len(strip_ansi(k)) for k, _ in pairs)
    return "\n".join(f"  {paint(k.rjust(klen), role)}  {paint(g('dot'), role)} {val}"
                     for k, val in pairs)


def bullet_list(items: Iterable[str], role: str = "accent") -> str:
    """`▸` orbital bullets, one item per line."""
    mark = paint(g("bullet"), role)
    return "\n".join(f"  {mark} {it}" for it in items)


def progress_bar(current: int, total: int, width: int = 24) -> str:
    """An orbital progress bar — filled ◉ in motion-teal, hollow ○ trailing."""
    total = max(total, 1)
    filled = max(0, min(width, round(current / total * width)))
    bar = paint(g("orbit") * filled, "go") + paint(g("orbit_hollow") * (width - filled), "muted")
    return f"{bar} {paint(f'{current}/{total}', 'muted')}"


def _status(kind: str, text: str) -> None:
    print(f"{seal(kind)} {text}")


def ok(text: str) -> None:
    """Print a success line: ``✓ text`` (teal seal)."""
    _status("ok", text)


def warn(text: str) -> None:
    """Print a warning line: ``▲ text`` (amber seal)."""
    _status("warn", text)


def err(text: str) -> None:
    """Print an error line: ``✗ text`` (crimson seal)."""
    _status("error", text)


def info(text: str) -> None:
    """Print an info line: ``• text``."""
    _status("info", text)
