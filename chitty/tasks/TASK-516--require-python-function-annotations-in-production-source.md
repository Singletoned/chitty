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

- [ ] With a temporary file at `src/chitty/_annotation_probe.py` defining `echo(value: str)` without a return annotation and returning `value`, `make check` fails with Ruff `ANN202` (the underscore-prefixed module is private); the same probe emits no annotation diagnostic before this change. Run `uv run ruff check --no-fix` on copies under `tests/` and `scripts/`: neither emits an annotation diagnostic.
- [ ] With the source probe annotated as `def echo(value: str) -> int:` while still returning `value`, `make check` gets past Ruff and fails in Pyright with a return-type diagnostic for the probe. Remove all probes; `make check` passes on the unchanged production source.

## Plan

Probe the existing Ruff behavior, configure the requested source-only annotation rules, then verify Ruff and Pyright with temporary probes and run formatting and checks before committing.

## Notes

Criterion 1 conflicts with Ruff behavior: the specified `src/chitty/_annotation_probe.py` containing `def echo(value: str):` and `return value` produced no diagnostic before the change, but after the requested configuration `make check` reports `ANN202 Missing return type annotation for private function`, not `ANN201`. Ruff treats the underscore-prefixed module as private. The planner must decide whether to expect `ANN202` for this fixture or specify a public module fixture for `ANN201`; the criterion cannot pass as written with the requested policy. The same probe under `tests/` and `scripts/` passed focused Ruff checks. With the source probe changed to return `int`, `make check` passed Ruff and Pyright reported `reportReturnType` for returning `str`. All probes were removed and `make check` passed 976 tests. The requested configuration is preserved in a commit; criterion 1 remains unverified as written.

Criterion 1 requires `ANN201` for `src/chitty/_annotation_probe.py`, but Ruff reports `ANN202` because the module is private. Planning must choose the intended diagnostic or a public module fixture before the criterion can be verified. Full probe evidence and the preserved implementation are recorded in the preceding note.

## History

- 2026-11-21T16:17:29Z honest-coral-heron → planning
- 2026-11-21T16:17:36Z honest-coral-heron: changed acceptance criteria
- 2026-11-21T16:17:36Z honest-coral-heron planning → cold-read
- 2026-11-21T16:20:32Z honest-coral-heron cold-read → planning
- 2026-11-21T16:20:45Z honest-coral-heron planning → todo
- 2026-11-21T16:24:19Z daring-hazel-eel todo → doing
- 2026-11-21T16:27:58Z daring-hazel-eel: wrote the plan
- 2026-11-21T16:30:04Z daring-hazel-eel: changed notes
- 2026-11-21T16:30:11Z daring-hazel-eel: changed owner, notes
- 2026-11-21T16:30:11Z daring-hazel-eel doing → planning
- 2026-11-21T16:40:52Z honest-coral-heron: changed acceptance criteria
- 2026-11-21T16:40:52Z honest-coral-heron planning → cold-read
- 2026-11-21T16:43:43Z honest-coral-heron cold-read → planning
- 2026-11-21T16:43:46Z honest-coral-heron planning → todo
- 2026-11-21T16:44:02Z jolly-umber-toad todo → doing
