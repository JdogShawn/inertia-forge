---
description: Implement the active task test-first with the Piston agent.
---

Adopt the **Piston** agent (`.claude/agents/piston.md`) and run the
**implementing-with-tdd** methodology (`.claude/skills/implementing-with-tdd/SKILL.md`).

Task: **$ARGUMENTS** (or the active task — `inertia-forge status`).

The TDD loop, per acceptance criterion:
1. **Red** — write a failing test; run it; see it fail for the right reason.
2. **Green** — minimal code to pass; run the task's verification command.
3. **Refactor** — clean up with tests green; `inertia-forge arch <changed>` must be
   0 P0; `inertia-forge sweep <changed>` clean.
4. Check the criterion off (`inertia-forge task ac`) and record the forge phase
   (`inertia-forge record-phase ...`).

Stay strictly within the task's scope. The session auto-closes only when every
blocking gate is green — there is no manual close.
