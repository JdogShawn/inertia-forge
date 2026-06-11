# Reviewing Code

> Judge a change for correctness and quality. Gates `check_correctness` and
> `check_security`. Evidence mode: `stamped` (output is findings, not code).
> Agent: **Caliper**.

## When to use
After a change is code-complete and before it merges; when a PR needs a rigorous
second read.

## The phases

### 1. read_changes
Read the entire diff before judging any part. Understand the intent and the plan
it claims to fulfill.

### 2. check_correctness  ⟂ blocking
- Does it do what the task's acceptance criteria require — no more, no less?
- Run the tests (`inertia-forge verify`). Run `inertia-forge arch` / `sweep` on
  changed files; their findings are evidence.
- Hunt the **absent**: the missing test, the unhandled `None`, the untaken error
  path, the off-by-one.

### 3. check_security  ⟂ blocking
Secrets, injection (f-string SQL / shell), unsafe deserialization, broad
`except: pass`, missing authz. `inertia-forge check` covers the deterministic part.

### 4. check_performance / check_style
Obvious complexity traps; naming; docs. Lower priority than 2–3.

### 5. provide_feedback
Report in **PEEL**: Point · Evidence (`file:line`) · Explanation · Link to the
criterion. Rank P0 (blocks) / P1 (fix first) / P2 (improve). No "looks good."

## Done
Every changed file measured, findings ranked + evidenced, and a clear verdict:
merge-ready or a precise must-fix list.
