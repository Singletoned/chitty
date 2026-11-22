---
title: Move the logged-command helpers from `run.py` into `commands.py`
status: doing
parent: TASK-343
created: 2026-11-21
---

## Description

Split from `TASK-343` on 2026-11-21. `TASK-343` will make `chitty edit -s review` (in `Repo.edit`, `src/chitty/store.py`) run the configured check, but the code that runs a logged command lives in `src/chitty/run.py`, which imports `store.py`. This ticket moves that code, unchanged in behaviour, into a new module both can use. Move only; no new behaviour.

Decisions:

- New module `src/chitty/commands.py`. It must not import `chitty.run` or `chitty.store` (it may import `chitty.errors`).
- Move these from `src/chitty/run.py` (checked on `main` 2026-11-21), dropping the leading underscore on functions: `RUN_LOG`, `RUN_LOG_EXCLUDE`, `AGENT_KILL_GRACE_SECONDS`, `_command_environment` → `command_environment`, `_terminate_process_tree` → `terminate_process_tree`, `_process_descendants` → `process_descendants`, `_running_processes` → `running_processes`, `_signal_process` → `signal_process`, `_with_exclude_line` → `with_exclude_line`, `_ignore_run_log` → `ignore_run_log`, `CommandTimedOut`, `_run_logged` → `run_logged`, and `_code_block` → `code_block`, and `_git` → `run_git` (below). Bodies stay the same except for the renamed calls.
- Also move `run.py`'s `_git` (near line 1542; it raises `ChittyError` with git's stderr only) as `run_git`, because `ignore_run_log` calls it. Its other callers in `run.py` (near lines 1124, 1134, 1141, 1194 and 1198) use `run_git` from `chitty.commands`. Do not add a new function to `src/chitty/git.py` and do not use `git._git_path` (it resolves symlinks and words errors differently), so every error message stays the same.
- `run.py` imports from `chitty.commands` every moved name it still uses (at least `command_environment`, `terminate_process_tree`, `run_logged`, `code_block`, `ignore_run_log`, `CommandTimedOut`, `RUN_LOG` and `run_git`) and keeps no definition of any old name. Every caller in `run.py` uses the new names.
- Update the tests that import the old names from `chitty.run` to import the new names from `chitty.commands` and use them at every call site (decided 2026-11-22: rename the calls too, no aliases); no other change: `tests/test_command_timeout.py`, `tests/test_next.py` (local imports near lines 1366, 1506 and 1512), `tests/test_property_runner_error_note.py` and `tests/test_property_run_log_exclude.py`. Run `git grep -n -w -e _run_logged -e _command_environment -e _code_block -e _terminate_process_tree -e _ignore_run_log -e _with_exclude_line -e _process_descendants -e _running_processes -e _signal_process -- src tests` afterwards to find any caller missed.

No property and no new test: a move that changes no behaviour; the existing tests above cover the moved code.

## Acceptance Criteria

- [ ] `src/chitty/commands.py` defines every moved name and imports neither `chitty.run` nor `chitty.store` (`git grep -n -e "chitty\.run" -e "chitty\.store" -- src/chitty/commands.py` finds nothing); the `git grep` in the Description finds no old name in `src` or `tests`, and `run.py` defines no `_git`
- [ ] The four updated test files pass with only their imports and the uses of moved names changed, and `make check` passes

## Plan

Correct the remaining test import to use commands, then run fix, formatting and checks before returning for review.

## Notes

The test requirements contradict each other: criterion 2 and the description require only import changes in the four test files, but criterion 1 requires no old names anywhere in `src` or `tests`. For example, `tests/test_command_timeout.py:29,43` calls `_run_logged`, and the other listed files likewise call `_run_logged`, `_ignore_run_log`, `_code_block`, or `_with_exclude_line`. Aliasing the imports would preserve those calls but fail the required grep; renaming the calls would violate the imports-only requirement. Please decide which requirement to change. I inspected the specified helper definitions and callers, including `_git` and the remaining listed tests; implementation and its verification cannot proceed until this is resolved.

Replanned 2026-11-22: tests rename their calls as well as imports; see the Description.

Review failed (work): A moved helper test still imports through the old module.
1: pass - Both specified git grep commands printed no matches; diff shows all moved definitions in commands.py and no run.py _git definition.
2: fail - Newly discovered: tests/test_command_timeout.py imports CommandTimedOut and run_logged from chitty.run, contrary to the description requiring moved names in all four files to be imported from chitty.commands. Change that import to chitty.commands. make check printed 1067 tests and OK, including these four files; the other test changes are limited to imports and renamed uses.

## Summary

Moved logged command helpers into commands.py and updated callers. make check passed: 1065 tests; old-name grep returned no matches.

## History

- 2026-11-21T23:24:34Z lively-zinc-newt → cold-read
- 2026-11-21T23:26:03Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-21T23:26:03Z lively-zinc-newt cold-read → todo
- 2026-11-22T00:41:06Z rosy-jade-crane todo → doing
- 2026-11-22T00:43:25Z rosy-jade-crane: changed owner, notes
- 2026-11-22T00:43:25Z rosy-jade-crane doing → planning
- 2026-11-22T00:43:55Z lively-zinc-newt: changed description, acceptance criteria, notes
- 2026-11-22T00:43:55Z lively-zinc-newt planning → todo
- 2026-11-22T00:44:58Z golden-bronze-gannet todo → doing
- 2026-11-22T00:47:11Z golden-bronze-gannet: wrote the plan
- 2026-11-22T00:50:07Z golden-bronze-gannet: changed summary
- 2026-11-22T00:50:07Z golden-bronze-gannet doing → review
- 2026-11-22T00:55:19Z upbeat-coral-jay: changed acceptance criteria, notes
- 2026-11-22T00:55:19Z upbeat-coral-jay review → doing
- 2026-11-22T00:59:34Z jolly-fawn-stoat: wrote the plan
