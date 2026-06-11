# Architecture Rules

The forge's `arch` check (and `file_analysis` evidence) enforce these limits.
Run `inertia-forge arch <path>` before completing any code task; fix every **P0**.

| Metric | Source files | Test files |
|--------|--------------|------------|
| Lines (P0 — error)   | > 400 | > 600 |
| Lines (P2 — warning) | > 200 | > 400 |
| Function length (P0) | > 50  | > 50  |
| Functions per file (P0) | > 15 | > 30 |
| Imports per file (P1)   | > 20 | > 40 |

Also flagged:
- `NotImplementedError` stubs claiming to be active code (P1)
- wildcard imports (P1)
- broad `except:`/`except Exception:` that swallow with `pass` (P2)
- `TODO` / `FIXME` / `HACK` / `XXX` markers (P2)
- unbounded `self.x = []`/`{}` collections without `maxlen`/`bounded` (P2)
- unused imports (`inertia-forge sweep`)

**Fixing violations**
- Function too long → extract named sub-steps or helpers.
- Too many functions / file too large → split hub-and-spoke; move helpers to
  `_helpers.py`, fixtures to `conftest.py`.
- After every extraction, run the tests — structure changes, behavior must not.
