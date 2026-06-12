"""Shared pytest fixtures.

Colour detection caches its answer at module scope, and the statusline CLI sets
FORCE_COLOR in its own process (correct for a one-shot command, but it would
leak between tests sharing one interpreter). This autouse fixture resets that
state after every test so colour assertions stay hermetic and order-independent.
"""
from __future__ import annotations

import os

import pytest

from inertia_forge import palette


@pytest.fixture(autouse=True)
def _reset_color_state():
    yield
    palette._TRUECOLOR = None
    palette._LIGHT = None
    os.environ.pop("FORCE_COLOR", None)
