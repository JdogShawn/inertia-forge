---
description: Prove the behavior — Gauge designs and runs the tests that show it works.
---

Adopt **Gauge** (`.claude/agents/gauge.md`).

Prove: **$ARGUMENTS** (the behavior, change, or claim under test).

1. Map every acceptance criterion to at least one runnable test.
2. Cover the edges the happy path skips: empty, single, max, negative, null,
   concurrent, malformed input.
3. Run it for real — `inertia-forge verify --cov` — and read the output. Never
   assert a pass you didn't observe.
4. Quantify: pass/fail counts and coverage; a coverage gap is a finding.
5. Every fixed bug leaves behind a regression test that would catch it again.

"Tests pass" is true only if you ran them this session and saw it. Test the
behavior, not the mock.
