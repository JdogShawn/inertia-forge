# Security Audit

> Scan for vulnerabilities, secrets, and dependency risk. Gates `scan_owasp` and
> `report`. Evidence mode: `stamped`. Agent: **Sentinel** (and **Bastion** to block).

## When to use
Before a release, after touching auth/input/subprocess/serialization, or on demand.

## The phases

### 1. scan_owasp  ⟂ blocking
Walk the OWASP-style surface: injection (SQL/shell/template), broken auth, secret
exposure, insecure deserialization, path traversal, SSRF, missing access control.
Deterministic baseline: `inertia-forge check` (secrets) — then read the high-risk
code by hand.

### 2. check_secrets
`inertia-forge scan-secrets` / `check`. Any hardcoded credential, key, or token is
a P0 — it does not ship.

### 3. check_deps
`inertia-forge scan-deps` (pip-audit). Known CVEs ranked by severity.

### 4. report  ⟂ blocking
Rank every finding by severity × likelihood with `file:line` evidence and a
concrete remediation. State coverage and gaps. Critical/High → escalate, don't
just describe.

## Honesty rule
Severity is reported as found — never soften a real High to a Medium. A finding
without a remediation is half a finding.

## Done
A ranked, evidenced, remediated report; nothing critical left merely described.
