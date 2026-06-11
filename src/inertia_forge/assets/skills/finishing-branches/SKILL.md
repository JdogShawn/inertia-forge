# Finishing Branches

> Take a code-complete branch to merge-ready. Gate `verify_tests`. Agents:
> **Caliper** (review), **Bastion** (safety), **Gauge** (tests).

## When to use
"Done", "ready to merge", "finish this branch", before a PR or a demo.

## The phases

### 1. verify_tests  ⟂ blocking
Full suite green by direct observation: `inertia-forge verify --cov`. Then the
project gate: `inertia-forge check . --tests tests/` — arch + secrets + tests in
one pass. Zero P0.

### 2. check_coverage
Coverage reported; any meaningful gap is a finding (route it to Gauge).

### 3. update_docs
README / changelog / docstrings reflect the change. Run `inertia-forge sweep` —
no dead imports left behind.

### 4. create_pr
A PR with: summary, the changes, test results (real numbers), security status
(`inertia-forge check` clean), and a checklist. Bastion clears it before it opens.

## Done
Branch is green end-to-end, the project gate passes, docs are current, and the PR
states real evidence — merge-ready, nothing hand-waved.
