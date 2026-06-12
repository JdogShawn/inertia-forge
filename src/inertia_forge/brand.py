"""INERTIA forge — branded marks: the atom, the wordmark, the banner.

The atom is INERTIA's sigil — orbits of motion around a still core, the picture
of inertia itself. The forge wears it. Taglines carry the doctrine: Newton's
first law for code quality, and the forge's own vow — *the only way out is
through*.
"""
from __future__ import annotations

import shutil
from typing import List

from inertia_forge.glyphs import g
from inertia_forge.palette import paint, strip_ansi

# The atom — 14 lines. Colour bands: teal motion top/bottom, violet at the
# equator where the orbit crosses. Each row is painted by its index in _BANDS.
_ATOM: List[str] = [
    "                    o",
    "              .ooo.  o  .ooo.",
    "           .o'     `'---'     `o.",
    "        .o'    .-----------.    `o.",
    "       /   .-'  \\    |    /  `-.   \\",
    "      ;   /      \\   |   /      \\   ;",
    "   ---|---\\       \\  |  /       /---|---",
    "      ;   \\       /  |  \\       /   ;",
    "       \\   `-.  /   |   \\  .-'   /",
    "        `o.   `-----+-----'   .o'",
    "           `o.      |      .o'",
    "              `o.   |   .o'",
    "                 `+-+-'",
    "                    |",
]
_BANDS = ["cyan", "cyan", "cyan_dark", "cyan_dark", "cyan", "cyan", "violet",
          "violet", "cyan", "cyan", "cyan_dark", "cyan_dark", "violet", "violet"]

TAGLINE = "Newton's first law for code quality."
VOW = "the only way out is through"


def logo(variant: str = "full") -> List[str]:
    """Return atom-logo lines. ``full`` (14-line), ``compact`` (3-line), ``tiny``."""
    if variant == "tiny":
        return [paint(g("atom"), "cyan", bold=True)]
    if variant == "compact":
        bar, node, core = g("orbit"), "o", g("orbit_hollow")
        return [paint(f"   {bar}---{node}---{bar}", "cyan", bold=True),
                paint("  /    |    \\", "cyan_dark"),
                paint(f" {core}-----+-----{core}", "violet")]
    return [paint(line, band, bold=(band == "cyan"))
            for line, band in zip(_ATOM, _BANDS)]


def wordmark() -> str:
    """`INERTIA FORGE` in spaced, motion-teal capitals."""
    return (paint("I N E R T I A", "cyan", bold=True) + "  "
            + paint("F O R G E", "violet", bold=True))


def _center(text: str, width: int) -> str:
    pad = max(0, (width - len(strip_ansi(text))) // 2)
    return " " * pad + text


def banner(version: str = "", subtitle: str = "", width: int = 0) -> str:
    """Compose the full startup banner: atom, wordmark, tagline, vow line."""
    width = width or min(shutil.get_terminal_size((80, 24)).columns, 80)
    art = logo("full")
    sub = subtitle or TAGLINE
    vow_line = paint(VOW, "muted", dim=True)
    ver = paint(f"v{version}", "accent", bold=True) if version else ""
    meta = f"{ver}  {paint(g('dot'), 'muted')}  {vow_line}" if ver else vow_line

    out: List[str] = ["", *art, "",
                      _center(wordmark(), width),
                      _center(paint(sub, "silver"), width),
                      _center(meta, width), ""]
    return "\n".join(out)


def mini_header(version: str = "") -> str:
    """One-line branded header: ⚛ INERTIA FORGE · vX — for command tops."""
    mark = paint(g("atom"), "cyan", bold=True)
    name = paint("INERTIA FORGE", "cyan", bold=True)
    ver = f"  {paint(g('dot'), 'muted')} {paint('v' + version, 'muted')}" if version else ""
    return f"{mark} {name}{ver}"
