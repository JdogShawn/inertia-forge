# Workflow

How we work here, on top of the forge loop (plan → build → review → ship).

## Branching
- Feature branches off `main`: `inertia-forge feature <name>`.

## Definition of done
- Acceptance criteria checked; `inertia-forge check . --tests tests/` is 0 P0;
  coverage reported; docs updated; Bastion cleared the PR.

## Conventions
- Tests live in `tests/`; helpers in `_helpers.py`; one job per module.
- Run `inertia-forge sweep` before committing — no dead imports.

## Releases
- `releasing-versions` skill: validate → bump → changelog → security → tag.
