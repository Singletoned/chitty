---
title: Move the logged-command helpers from `run.py` into `commands.py`
status: cold-read
parent: TASK-343
created: 2026-11-21
---

## Description

Split from `TASK-343` on 2026-11-21. `TASK-343` will make `chitty edit -s review` (in `Repo.edit`, `src/chitty/store.py`) run the configured check, but the code that runs a logged command lives in `src/chitty/run.py`, which imports `store.py`. This ticket moves that code, unchanged in behaviour, into a new module both can use. Move only; no new behaviour.

Decisions:

- New module `src/chitty/commands.py`. It must not import `chitty.run` or `chitty.store` (it may import `chitty.git` and `chitty.errors`).
- Move these from `src/chitty/run.py` (checked on `main` 2026-11-21), dropping the leading underscore on functions: `RUN_LOG`, `RUN_LOG_EXCLUDE`, `AGENT_KILL_GRACE_SECONDS`, `_command_environment` → `command_environment`, `_terminate_process_tree` → `terminate_process_tree`, `_process_descendants` → `process_descendants`, `_running_processes` → `running_processes`, `_signal_process` → `signal_process`, `_with_exclude_line` → `with_exclude_line`, `_ignore_run_log` → `ignore_run_log`, `CommandTimedOut`, `_run_logged` → `run_logged`, and `_code_block` → `code_block`. Bodies stay the same except for the renamed calls.
- `ignore_run_log` calls `run.py`'s private `_git` today. In `commands.py` use a new public `git.git_path(root: Path, name: str) -> Path` in `src/chitty/git.py`: it returns `root / <git rev-parse --git-path name>` when that output is relative, else the output as a `Path`, raising `ChittyError` as `_git` in `git.py` does. `rebase_in_progress` may keep its own code.
- `run.py` imports the moved names from `chitty.commands` and keeps no definition of any old name. Every caller in `run.py` uses the new names.
- Update the tests that import the old names from `chitty.run` to import the new names from `chitty.commands`, with no other change: `tests/test_command_timeout.py`, `tests/test_next.py` (local imports near lines 1366, 1506 and 1512), `tests/test_property_runner_error_note.py` and `tests/test_property_run_log_exclude.py`. Run `git grep -n -e _run_logged -e _command_environment -e _code_block -e _terminate_process_tree -e _ignore_run_log -e _with_exclude_line -- src tests` afterwards to find any caller missed.

No property and no new test: a move that changes no behaviour; the existing tests above cover the moved code.

## Acceptance Criteria

- [ ] `src/chitty/commands.py` defines every moved name and imports neither `chitty.run` nor `chitty.store` (`git grep -n -e "chitty.run" -e "chitty.store" -- src/chitty/commands.py` finds nothing); the `git grep` in the Description finds no old name in `src` or `tests`
- [ ] The four updated test files pass with only their imports changed, and `make check` passes

## History

- 2026-11-21T23:24:34Z lively-zinc-newt → cold-read
