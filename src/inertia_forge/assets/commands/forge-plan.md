---
description: Plan a feature with the Vector agent — intent into a gated plan + tasks.
---

Adopt the **Vector** agent (`.claude/agents/vector.md`) and run the
**designing-and-implementing** methodology (`.claude/skills/designing-and-implementing/SKILL.md`).

Goal: **$ARGUMENTS**

1. Clarify the goal and constraints until unambiguous — ask, don't assume.
2. Survey the codebase to ground the plan; cite `file:line`.
3. Propose the smallest approach that fully solves it; name the failure modes it
   prevents. Recommend one.
4. Materialize tasks in the forge — each with acceptance criteria, a complexity
   estimate, and a verification command:
   `inertia-forge task plan ...` then `inertia-forge task add ...`.
5. Confirm with `inertia-forge task budget` (every task estimated) before handing
   off to Piston.

Do NOT write implementation code — that's Piston's job.
