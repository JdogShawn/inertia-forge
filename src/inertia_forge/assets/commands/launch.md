---
description: Launch the branch — finish to merge-ready, Bastion clears the gate.
---

Run **finishing-branches** (`.claude/skills/finishing-branches/SKILL.md`) with
**Bastion** (`.claude/agents/bastion.md`) clearing safety.

Launch: **$ARGUMENTS** (or the current branch).

1. **Project gate**: `inertia-forge check . --tests tests/ --deps` — arch +
   secrets + tests + dependency audit, zero P0.
2. **Coverage**: `inertia-forge verify --cov <pkg>`; name any meaningful gap.
3. **Sweep**: `inertia-forge sweep .` — no dead imports left behind.
4. **Bastion clears** the commit/PR: no secrets, no destructive ops, no gate
   bypass.
5. Open the PR with real evidence — summary, changes, test numbers, security
   status.

Do not declare merge-ready on anything you didn't run this session.
