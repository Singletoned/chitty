---
title: Report all missing run configuration before starting
status: blocked
owner: human
created: 2026-11-13
---

## Description

When `chitty run` starts, preflight every required `chitty.toml` field and report all missing values in one error. This repository first failed on missing `setup = "make install"`, then on missing `check = "make check"`; sequential validation caused two avoidable failed invocations. Include example configuration for each missing field.

## Acceptance Criteria

- [x] When multiple static run settings are missing, `chitty run` fails before setup, ticket selection, or agent launch and reports every missing setting in one error, with an example configuration line for each; the regression fails against the current implementation.
- [x] The preflight still reports the correct `chitty.toml` or `pyproject.toml` source and preserves existing validation for invalid or incomplete agent commands.
- [x] The `chitty run` documentation describes the required configuration and shows example values for every preflight setting.

## Plan

Update run preflight to collect every missing required setting before raising, preserving the selected config source and including a concrete TOML example for each setting. Add a regression test that removes multiple required settings and asserts one error lists all of them and their examples, then update the runner documentation to describe the preflight and configuration examples. Run the regression against the current implementation first, then format and full checks.

## Notes

Suggestion origin: injustice-league

Regression test failed before the implementation: `test_run_reports_all_missing_preflight_settings_together` received only the missing `setup` error. After the fix, it reports missing `setup`, `check`, and `agent_command` together, with examples, and does not create a worktree. Focused preflight tests pass. `make format && make check` passed: 524 Python tests, Ruff, Pyright, and Node tests.

Review blocked: TASK-315 has no branch `task-315`. A person must restore the branch or choose the ticket's final state.

## Summary

Implemented and committed as 5499298 (Task: TASK-315). `chitty run` now preflights all static required configuration, reports every missing setting in one error with examples, and names the config source. Added regression coverage and documented the required configuration and preflight behavior. Verification: regression failed before the fix; focused tests and `make format && make check` pass. No follow-ups.

## History

- 2026-11-13T14:02:36Z zesty-umber-puffin → backlog
- 2026-11-13T14:02:37Z zesty-umber-puffin: changed notes
- 2026-11-13T14:03:18Z zesty-umber-puffin: changed acceptance criteria; wrote the plan
- 2026-11-13T14:03:18Z zesty-umber-puffin backlog → doing
- 2026-11-13T14:06:21Z zesty-umber-puffin: changed notes, summary; ticked acceptance criteria
- 2026-11-13T14:06:21Z zesty-umber-puffin doing → review
- 2026-11-13T14:23:43Z plucky-dusky-gannet: changed owner, notes
- 2026-11-13T14:23:43Z plucky-dusky-gannet review → blocked
