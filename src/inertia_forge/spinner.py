"""INERTIA forge — orbital spinner for long operations (pytest, dep scans).

Opt-in and TTY-gated: under NO_COLOR, a pipe, or a narrow encoding it renders
nothing, so logs stay clean. The forge's deterministic output never depends on
it — it's pure progress affordance.
"""
from __future__ import annotations

import sys
import threading
import time
from typing import List, Optional

from inertia_forge.glyphs import _can_encode
from inertia_forge.palette import paint, supports_color

_FRAMES = {
    "orbital": ["◜", "◝", "◞", "◟"],
    "atom": ["○", "◔", "◑", "◕", "●", "◕", "◑", "◔"],
    "token": ["●", "·", "∙", "∘", "○", "◦", "·", "∙"],
}


class Spinner:
    """A background orbital spinner; use as a context manager.

    >>> with Spinner("running tests", variant="atom"):
    ...     run_pytest()
    """

    def __init__(self, label: str = "", variant: str = "orbital",
                 role: str = "accent", interval: float = 0.09) -> None:
        frames = _FRAMES.get(variant, _FRAMES["orbital"])
        self._frames: List[str] = frames if _can_encode("".join(frames)) else ["-", "\\", "|", "/"]
        self._label = label
        self._role = role
        self._interval = interval
        self._idx = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._active = supports_color() and sys.stdout.isatty()

    def _loop(self) -> None:
        while self._running:
            frame = paint(self._frames[self._idx % len(self._frames)], self._role, bold=True)
            sys.stdout.write(f"\r{frame} {self._label}")
            sys.stdout.flush()
            self._idx += 1
            time.sleep(self._interval)

    def __enter__(self) -> "Spinner":
        if self._active:
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()
        return self

    def __exit__(self, *_exc) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=self._interval * 2)
        if self._active:
            sys.stdout.write("\r" + " " * (len(self._label) + 4) + "\r")
            sys.stdout.flush()
