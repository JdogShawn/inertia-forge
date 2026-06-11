---
description: Drive the task to green — Piston implements test-first.
---

Adopt **Piston** (`.claude/agents/piston.md`); run **implementing-with-tdd**
(`.claude/skills/implementing-with-tdd/SKILL.md`).

Task: **$ARGUMENTS** (or the active task — `inertia-forge status`).

Per acceptance criterion, run the loop:
1. **Red** — a failing test; run it; see it fail for the right reason.
2. **Green** — minimal code to pass; run the task's verification command.
3. **Refactor** — clean up, tests green; `inertia-forge arch <changed>` 0 P0;
   `inertia-forge sweep <changed>` clean.
4. Check the criterion (`inertia-forge task ac`); record the phase
   (`inertia-forge record-phase ...`).

Stay in scope. The session closes only when every blocking gate is green.
