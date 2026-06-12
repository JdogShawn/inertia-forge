"""INERTIA forge — colour core.

The forge speaks INERTIA's visual language: teal motion (#00FFD1 → #00C9A7),
violet thought (#a78bfa), amber caution, crimson stop. Pure stdlib, zero deps.

Honours NO_COLOR (https://no-color.org/), TERM=dumb, non-TTY, and FORCE_COLOR.
Truecolor (24-bit) when the terminal advertises it, otherwise plain text — the
forge never emits an escape a terminal can't read. Light-mode aware via env.
"""
from __future__ import annotations

import os
import re
import sys
from typing import Tuple

RESET = "\x1b[0m"
BOLD = "\x1b[1m"
DIM = "\x1b[2m"
ITALIC = "\x1b[3m"

# Brand palette — RGB. The motion gradient (cyan→cyan_dark) is the signature.
PALETTE: dict[str, Tuple[int, int, int]] = {
    "cyan": (0, 255, 209),        # #00FFD1 — primary / accent / "go"
    "cyan_dark": (0, 201, 167),   # #00C9A7 — success / gradient end
    "violet": (167, 139, 250),    # #a78bfa — thought / secondary
    "violet_dark": (124, 58, 237),# #7c3aed
    "amber": (255, 184, 0),       # #ffb800 — warning
    "gold": (255, 215, 0),        # #ffd700 — title accent
    "crimson": (255, 62, 94),     # #ff3e5e — error / stop
    "pale_blue": (159, 185, 255), # #9fb9ff — info
    "white": (224, 224, 224),     # #e0e0e0 — primary text
    "silver": (136, 146, 176),    # #8892b0 — secondary text
    "gray": (139, 148, 158),      # #8b949e — muted
    "gray_mid": (74, 79, 88),     # #4a4f58 — borders / rules
    "bronze": (205, 127, 50),     # #cd7f32 — frame accent
}

# Semantic roles → palette key. Commands speak in roles, not hex.
ROLES: dict[str, str] = {
    "accent": "cyan", "success": "cyan_dark", "go": "cyan",
    "think": "violet", "warn": "amber", "error": "crimson",
    "info": "pale_blue", "title": "gold", "text": "white",
    "muted": "gray", "border": "gray_mid", "frame": "bronze",
}

# In a light terminal these dark-tuned tones wash out; swap for readable ones.
_LIGHT_REMAP: dict[str, Tuple[int, int, int]] = {
    "white": (26, 26, 26), "silver": (60, 60, 60), "gray": (90, 90, 90),
    "gold": (154, 107, 0), "amber": (138, 90, 0), "cyan": (0, 128, 105),
}

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_TRUECOLOR: bool | None = None
_LIGHT: bool | None = None


def supports_color() -> bool:
    """True when styled output is appropriate for the current stdout."""
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if os.environ.get("TERM") == "dumb":
        return False
    return sys.stdout.isatty()


def supports_truecolor() -> bool:
    """True when the terminal advertises 24-bit colour."""
    global _TRUECOLOR
    if _TRUECOLOR is not None:
        return _TRUECOLOR
    if not supports_color():
        _TRUECOLOR = False
    elif os.environ.get("FORCE_COLOR") in ("3", "truecolor"):
        _TRUECOLOR = True
    else:
        ct = os.environ.get("COLORTERM", "").lower()
        term = os.environ.get("TERM", "").lower()
        _TRUECOLOR = (ct in ("truecolor", "24bit")
                      or any(s in term for s in ("truecolor", "24bit", "kitty", "direct")))
    return _TRUECOLOR


def _light_mode() -> bool:
    """Best-effort light-terminal detection (env-only, deterministic)."""
    global _LIGHT
    if _LIGHT is not None:
        return _LIGHT
    v = (os.environ.get("INERTIA_FORGE_LIGHT") or "").strip().lower()
    if v in ("1", "true", "yes", "on"):
        _LIGHT = True
    elif v in ("0", "false", "no", "off"):
        _LIGHT = False
    else:
        cfgbg = (os.environ.get("COLORFGBG") or "").split(";")[-1].strip()
        _LIGHT = cfgbg.isdigit() and int(cfgbg) in (7, 15)
    return _LIGHT


def rgb_for(name: str) -> Tuple[int, int, int]:
    """Resolve a role or palette name to an (r,g,b), light-mode adjusted."""
    key = ROLES.get(name, name)
    if _light_mode() and key in _LIGHT_REMAP:
        return _LIGHT_REMAP[key]
    return PALETTE.get(key, PALETTE["white"])


def fg(name: str) -> str:
    """Foreground escape for a role/palette name (empty if no truecolor)."""
    if not supports_truecolor():
        return ""
    r, g, b = rgb_for(name)
    return f"\x1b[38;2;{r};{g};{b}m"


def paint(text: str, *roles: str, bold: bool = False, dim: bool = False) -> str:
    """Wrap *text* in the given role colour + attributes, then reset.

    A no-op (returns text unchanged) when colour is disabled, so callers can
    paint unconditionally and trust NO_COLOR / pipes to stay clean.
    """
    if not supports_color():
        return text
    lead = "".join(fg(r) for r in roles if r)
    if bold:
        lead += BOLD
    if dim:
        lead += DIM
    return f"{lead}{text}{RESET}" if lead else text


def strip_ansi(text: str) -> str:
    """Remove every ANSI SGR sequence — for width math and plain fallbacks."""
    return _ANSI_RE.sub("", text)
