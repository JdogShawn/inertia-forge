# Designing and Implementing

> The full feature flow: clarify → design → plan tasks → implement → verify.
> Gates `clarify_requirements`, `plan_tasks` (task_management), `verify`.
> Agents: **Vector** (design/plan) then **Piston** (implement) then **Gauge/Caliper**.

## When to use
"Build a…", "add a…", "create a…" — anything that starts from intent rather than a
ready task.

## The phases

### 1. clarify_requirements  ⟂ blocking
Restate the goal and constraints; resolve every ambiguity with the user. Zero
ambiguity tolerance — a vague spec produces vague code.

### 2. design_approach
Survey the codebase. Propose the smallest approach that fully solves it; name the
trade-offs and the failure modes it prevents. Recommend one.

### 3. plan_tasks  ⟂ blocking (verified against real task state)
Create tasks in the forge — each with acceptance criteria, a complexity estimate,
and a verification command. `inertia-forge task add ...` (or `ignite <backlog>`).
The gate verifies the tasks actually exist and are well-formed.

### 4. implement
For each task, run the **implementing-with-tdd** skill (Piston). Stay within the
task's scope.

### 5. verify  ⟂ blocking
Full suite green (`inertia-forge verify --cov`), `arch` clean, acceptance criteria
all checked. Caliper reviews; Gauge proves behavior.

## Done
Intent became a gated plan, the plan became tested code, and every gate closed on
real evidence.
