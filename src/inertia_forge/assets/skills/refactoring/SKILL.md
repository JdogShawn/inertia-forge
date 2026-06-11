# Refactoring

> Improve structure without changing behavior. Gate `verify`. Agent: **Piston**
> (with **Gauge** holding the behavior line).

## When to use
A function over 50 lines, a file over 400, duplicated logic, a name that lies, a
module doing two jobs. `inertia-forge arch` / `sweep` flag most of these.

## The phases

### 1. scan
Find the targets: `inertia-forge arch <path>` (size/length/count), `inertia-forge
sweep <path>` (dead imports). List them by severity.

### 2. split_files / reduce_functions
Extract helpers to `_helpers.py`; split a god-file hub-and-spoke; pull a long
function into named sub-steps. **One refactor at a time.**

### 3. verify  ⟂ blocking
After **every** extraction, run the tests (`inertia-forge verify`) — behavior must
be byte-identical. If a test changes, you changed behavior; that's not a refactor.
Re-run `arch` until clean.

## The rule
Refactoring changes structure, never behavior. If you need to change behavior,
that's the implementing-with-tdd skill — switch to it and write the test first.

## Done
The structural debt is gone, `arch`/`sweep` are clean, and the test suite is
exactly as green as before you started — no behavior drift.
