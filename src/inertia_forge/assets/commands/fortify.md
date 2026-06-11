---
description: Fortify — Sentinel audits security, Bastion blocks what's dangerous.
---

Adopt **Sentinel** (`.claude/agents/sentinel.md`) for the audit and **Bastion**
(`.claude/agents/bastion.md`) for the gate; run **security-audit**
(`.claude/skills/security-audit/SKILL.md`).

Target: **$ARGUMENTS** (or the whole project).

1. Deterministic baseline: `inertia-forge check` (secrets) and
   `inertia-forge scan-deps` (CVEs). Treat their output as ground truth.
2. Read the high-risk surfaces by hand — auth, input handling, subprocess, file
   I/O, network, serialization.
3. Rank every finding by severity × likelihood with `file:line` and a concrete
   remediation. State coverage and gaps.
4. **Bastion** blocks anything dangerous from proceeding; critical/high findings
   escalate, they don't just get described.

Severity is reported as found — never softened.
