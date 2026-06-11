---
description: Chart the course — Vector turns intent into a gated plan + tasks.
---

Adopt **Vector** (`.claude/agents/vector.md`); run **designing-and-implementing**
(`.claude/skills/designing-and-implementing/SKILL.md`).

Chart: **$ARGUMENTS**

1. Clarify the goal and constraints until unambiguous — ask, don't assume.
2. Survey the codebase to ground the plan; cite `file:line`.
3. Propose the smallest approach that fully solves it; name the failure modes it
   prevents; recommend one.
4. Lay the tasks into the forge — each with acceptance criteria, a complexity
   estimate, and a verification command: `inertia-forge task plan ...` →
   `inertia-forge task add ...`.
5. Confirm with `inertia-forge task budget` before handing off to **drive**.

Set the direction; do not write implementation code.
