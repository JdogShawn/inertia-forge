"""INERTIA forge — glyph vocabulary.

Orbital marks (◉ ○), motion arrows, gate seals, status seals. Every glyph has
an ASCII twin: if the terminal's encoding can't render the Unicode form (e.g.
Windows cp1252), the forge falls back instead of crashing — the lesson from the
doctor cp1252 incident, baked into the type.
"""
from __future__ import annotations

import sys

from inertia_forge.palette import paint

# name -> (unicode, ascii-fallback)
_GLYPHS: dict[str, tuple[str, str]] = {
    "atom": ("⚛", "*"),          # ⚛ the brand mark
    "orbit": ("◉", "(o)"),       # ◉ filled orbital
    "orbit_hollow": ("○", "( )"),# ○ hollow orbital
    "ok": ("✓", "OK"),           # ✓
    "warn": ("▲", "!!"),         # ▲
    "error": ("✗", "XX"),        # ✗
    "info": ("•", "-"),          # •
    "gate_locked": ("▣", "[#]"), # ▣ a sealed gate
    "gate_open": ("▢", "[ ]"),   # ▢ a cleared gate
    "arrow_r": ("→", "->"),      # →
    "arrow_l": ("←", "<-"),      # ←
    "bullet": ("▸", ">"),        # ▸
    "dot": ("·", "."),           # ·
    "spark": ("✦", "*"),         # ✦
}

# semantic seal -> (glyph name, colour role)
_SEALS: dict[str, tuple[str, str]] = {
    "ok": ("ok", "success"), "success": ("ok", "success"),
    "warn": ("warn", "warn"), "error": ("error", "error"),
    "info": ("info", "info"), "locked": ("gate_locked", "warn"),
    "open": ("gate_open", "success"),
}


def _can_encode(s: str) -> bool:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        s.encode(enc)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def g(name: str) -> str:
    """The best renderable form of a named glyph for this terminal."""
    uni, ascii_ = _GLYPHS.get(name, ("", ""))
    return uni if uni and _can_encode(uni) else ascii_


def seal(kind: str) -> str:
    """A coloured status seal, e.g. ``✓`` in success-teal or ``✗`` in crimson."""
    glyph_name, role = _SEALS.get(kind, ("info", "info"))
    return paint(g(glyph_name), role, bold=True)


def badge(text: str, role: str = "accent") -> str:
    """A compact chip — `· TEXT ·` painted in *role*, for inline status."""
    dot = g("dot")
    return paint(f"{dot} {text} {dot}", role, bold=True)


def gate_badge(state: str) -> str:
    """Render a gate's state as a sealed/cleared mark with a label."""
    if state in ("open", "green", "clear", "passed"):
        return f"{seal('open')} {paint('CLEAR', 'success', bold=True)}"
    return f"{seal('locked')} {paint('SEALED', 'warn', bold=True)}"
