---
title: Stop clearing `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` in `chitty run`
status: done
created: 2026-11-17
---

## Description

`TASK-238` made `chitty run` remove `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` from the environment of the agent and of the setup, check and landing-check commands, because one person's shell exported them pointing at a shared environment. That shell has since been fixed, and the human decided (`HUMAN-10`, 2026-11-17) that no other users should hit it. Remove the code.

- In `_command_environment` in `src/chitty/run.py` (or, if `TASK-343` has landed, `command_environment` in `src/chitty/commands.py`, where it moves unchanged), delete the two `pop` lines for `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT`. Keep the `CHITTY_USAGE_FILE` pop and its comment. Change the docstring to `Copy the environment without an inherited usage file.`
- Delete `tests/test_run_environment.py`: all three of its tests assert the two variables are removed.
- In `test_run_uses_runner_chitty_and_strips_worktree_environment` in `tests/test_next.py`, remove the parts that set, record and check `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT`. Keep its `PATH` and runner-`chitty` assertions. Make it also set `CHITTY_USAGE_FILE` in the parent environment (restored afterwards, as it restores the others now) and keep its assertion that the agent sees none. Rename it `test_run_uses_runner_chitty_and_drops_usage_file`.
- No test sets `CHITTY_USAGE_FILE` today, so the existing `usage_file` assertion passes even without the pop. The changed test must fail when the `CHITTY_USAGE_FILE` pop is removed.
- This repository's `Makefile` exports `UV_PROJECT_ENVIRONMENT` and `VIRTUAL_ENV` as each checkout's own `.venv`, so `make` in a worktree keeps using that worktree's environment. Leave the `Makefile` alone.
- Leave `chitty.toml` alone: branches must not edit it. After this lands, the planning session removes the `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT` prefix and its comment from `agent_command` and `[agent_commands]` on `main` by hand.

No property tests: this removes code, and the remaining behaviour (removing `CHITTY_USAGE_FILE`) is a single environment key.

## Acceptance Criteria

- [x] `git grep -n "VIRTUAL_ENV\|UV_PROJECT_ENVIRONMENT" -- src tests` finds nothing except phrases in `tests/test_guide_read_only_cold_read.py` that do not concern the runner environment, and `tests/test_run_environment.py` is gone
- [x] `test_run_uses_runner_chitty_and_drops_usage_file` sets `CHITTY_USAGE_FILE` in the parent environment and passes, and fails with the `CHITTY_USAGE_FILE` pop removed, shown in a note; `make check` passes

## Plan

Update run environment construction to preserve inherited virtual-environment variables while continuing to remove CHITTY_USAGE_FILE. First adjust the next-run integration test to set and verify the usage-file behavior and remove its virtual-environment assertions; run it against current behavior and verify it fails for the missing parent variable setup expectation. Then remove the obsolete environment tests and implementation pops, run formatting and make check, and commit the implementation.

## Notes

Cold read by a Haiku subagent, 2026-11-17. Fixed: criterion 2 passed with nothing built (no test set `CHITTY_USAGE_FILE`); the leftover `tests/test_run_environment.py` and its helper; a wrong claim of a comment on the two pops; the stale docstring; the conditional rename; the `commands.py` alternative (`TASK-343` has not landed, and its move keeps the function body). Checked: the `Makefile` exports each checkout's own `.venv`, so removing the pops does not change `make check` in a worktree. The `chitty.toml` step after landing is the planning session's, by hand.

Regression evidence: the updated focused test passed with the CHITTY_USAGE_FILE pop, then failed when that pop was temporarily removed (agent observed /parent/usage.jsonl); the pop was restored.

Reviewed:
1: pass - `git grep -n "VIRTUAL_ENV\|UV_PROJECT_ENVIRONMENT" -- src tests` returned only the permitted guide test; `tests/test_run_environment.py` is absent.
2: pass - `make check` passed 614 tests; the focused unittest printed OK with the pop and FAILED with `AssertionError: '/parent/usage.jsonl' is not None` when the pop was removed, then restored.

## Summary

Removed clearing of VIRTUAL_ENV and UV_PROJECT_ENVIRONMENT from _command_environment; retained CHITTY_USAGE_FILE removal and updated its docstring. Deleted obsolete environment tests and updated the runner integration test. Verification: focused test passed; it failed with the usage-file pop temporarily removed; make check passed (614 tests); git grep found only the permitted guide-test phrases. chitty fix TASK-365 was attempted but the CLI rejected this task path as not a task file in any context. No follow-ups beyond the planned main-branch chitty.toml cleanup.

## History

- 2026-11-17T17:26:19Z kind-umber-toad → planning
- 2026-11-17T19:53:43Z kind-umber-toad: changed owner
- 2026-11-17T19:53:43Z kind-umber-toad planning → cold-read
- 2026-11-17T19:55:02Z kind-umber-toad: changed description, acceptance criteria, notes
- 2026-11-17T19:55:02Z kind-umber-toad cold-read → planning
- 2026-11-17T19:55:17Z kind-umber-toad: changed description
- 2026-11-17T22:01:52Z kind-umber-toad: changed owner
- 2026-11-17T22:01:52Z kind-umber-toad planning → todo
- 2026-11-17T22:36:57Z open-russet-ibis todo → doing
- 2026-11-17T22:37:11Z open-russet-ibis: wrote the plan
- 2026-11-17T22:38:38Z open-russet-ibis: changed notes, summary; ticked acceptance criteria
- 2026-11-17T22:38:38Z open-russet-ibis doing → review
- 2026-11-17T22:40:29Z brisk-teal-toad: changed notes
- 2026-11-17T22:40:29Z brisk-teal-toad review → done
