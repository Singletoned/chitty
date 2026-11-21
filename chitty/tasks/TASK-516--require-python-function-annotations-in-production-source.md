---
title: Require Python function annotations in production source
status: doing
created: 2026-11-21
---

## Description

Production Python already passes a missing-annotation audit, and `make check` already runs Pyright (strict on `src`, standard on `tests`). But inferred return types can pass Pyright even where an explicit signature is wanted. Make explicit annotations a standard lint requirement on production functions without changing Pyright or imposing the requirement on tests and scripts.

In `pyproject.toml`, extend the existing Ruff lint selection with `ANN001`, `ANN002`, `ANN003`, `ANN201`, `ANN202`, `ANN204`, `ANN205`, and `ANN206`. Scope those rules to `src/` using a negated per-file ignore (`"!src/**" = ["ANN"]`). Require explicit parameter types (except implicit method receivers) and explicit return types for public, private and special functions, including class and static methods. Keep the existing `make check` and CI wiring: Ruff checks that annotations are present; Pyright checks their correctness. No runtime behavior, new dependency, checker configuration change, or bulk reannotation of tests or scripts.

Use temporary probe files in the worker's isolated worktree and remove them before committing. No new application test or property: the rule set is fixed third-party lint policy, and the standard check itself is the ongoing regression gate. Record the probe outputs as review evidence rather than adding tests for Ruff's implementation.

## Acceptance Criteria

- [ ] With a temporary file at `src/chitty/_annotation_probe.py` containing `def echo(value: str):` and `return value`, `make check` fails with Ruff `ANN201`; the same probe does not produce that diagnostic before this change. Re-run the focused Ruff command with the same file contents under `tests/` and `scripts/`: neither emits an annotation diagnostic.
- [ ] With the source probe annotated as `def echo(value: str) -> int:` while still returning `value`, `make check` gets past Ruff and fails in Pyright with a return-type diagnostic for the probe. Remove all probes; `make check` passes on the unchanged production source.

## History

- 2026-11-21T16:17:29Z honest-coral-heron → planning
- 2026-11-21T16:17:36Z honest-coral-heron: changed acceptance criteria
- 2026-11-21T16:17:36Z honest-coral-heron planning → cold-read
- 2026-11-21T16:20:32Z honest-coral-heron cold-read → planning
- 2026-11-21T16:20:45Z honest-coral-heron planning → todo
- 2026-11-21T16:24:19Z daring-hazel-eel todo → doing
