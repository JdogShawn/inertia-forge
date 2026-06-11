---
description: Calibrate the change against the spec — Caliper reviews precisely.
---

Adopt **Caliper** (`.claude/agents/caliper.md`); run **reviewing-code**
(`.claude/skills/reviewing-code/SKILL.md`).

Calibrate: **$ARGUMENTS** (or the current diff: `git diff`).

1. Read the whole change before judging any part.
2. Verify, don't trust — `inertia-forge verify`, `inertia-forge arch`,
   `inertia-forge sweep` on the changed files. Their findings are evidence.
3. Check against the task's acceptance criteria — nothing more, nothing less.
4. Hunt the absent: the missing test, the unhandled None, the untaken error path.
5. Report in **PEEL** (Point · Evidence `file:line` · Explanation · Link), ranked
   P0 / P1 / P2. No "looks good."

Verdict: merge-ready, or the precise must-fix list.
