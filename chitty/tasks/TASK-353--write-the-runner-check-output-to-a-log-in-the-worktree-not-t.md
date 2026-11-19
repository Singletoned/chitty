---
title: Write the runner check output to a log in the worktree, not the ticket
status: planning
priority: high
created: 2026-11-16
---

## Description

The runner writes the full output of the configured `check` into ticket notes (`_run_check` and `_handle_check_failure` in `src/chitty/run.py`), once in the `Runner error (check): ...` line and again in its `Error output:` block. A failing run puts hundreds of lines into the ticket. Decided with the owner 2026-11-19: command output never goes into tickets. It goes to a log file in the worktree, overwritten by every run, so the file always holds the last run.

Decisions:

- Module constants in `src/chitty/run.py`: `RUN_LOG = Path(".chitty/check.log")` (relative to the worktree) and `RUN_LOG_EXCLUDE = "/.chitty/"`.
- The log is ignored through Git's shared exclude file, not `.gitignore`, so no committed file and no `chitty init` change is needed: `_ignore_run_log(worktree: Path) -> None` finds the file with `git rev-parse --git-path info/exclude` run in the worktree (this resolves to the common Git directory, which every linked worktree reads; checked by hand 2026-11-19), creates it and its directory if missing, and appends `RUN_LOG_EXCLUDE` on its own line only when no line already equals it.
- `_run_logged(phase: str, command: str, worktree: Path) -> int` calls `_ignore_run_log`, creates `.chitty/`, opens `RUN_LOG` for writing (truncating it), writes `# chitty <phase>: <command>` and a newline, flushes, runs `shlex.split(command)` with `cwd=worktree`, `stdin=subprocess.DEVNULL`, `env=_command_environment()`, stdout to the open file and `stderr=subprocess.STDOUT`, then writes `# exit <returncode>` and a newline and returns the return code. `FileNotFoundError` is not caught there; callers keep their `command not found` handling. `KeyboardInterrupt` handling stays in the callers.
- `_run_check` uses `_run_logged("check", ...)` and never captures output. Its failure detail is exactly `` check exited with status <N>; output in `.chitty/check.log` `` (backticks included), used both by `Runner error (check)` and by `Check failed before this session: ...`. The `command not found` text is unchanged.
- The log is written on success as well, so it always reflects the last run.
- Out of scope: `setup` and the landing check (`TASK-426`), and the repeated `Error output:` block for other errors (`TASK-427`).
- Update the sentences in `docs/plan/next-action-and-runner.md` that say check output goes into the note.

Tests: change the existing tests in `tests/test_next.py` as below, and add one. `worktree` is `self.root / ".worktrees/task-1"`; `log` is `(worktree / ".chitty/check.log").read_text()`. No property: fixed runner runs with real Git.

- `test_run_check_failure_on_todo_ticket_records_error_on_branch`: the two `assertIn("check line 6", ...)` become `assertNotIn` (task notes and `branch_ticket`). Add: `branch_ticket` contains `` output in `.chitty/check.log` ``; `log` starts with `# chitty check: `, contains `check line 6\n` and ends with `# exit 1\n`; `git -C <worktree> status --short --untracked-files=all` output does not contain `.chitty`. The existing `?? check-args` assertion stays.
- `test_run_check_failure_records_markdown_like_output`: the two `assertIn(..., notes)` become `assertNotIn`; `log` contains `FAIL: test_something\n`, a line that is exactly three backticks, and `# not a heading\n`.
- `test_run_check_failure_on_doing_ticket_starts_agent` and `test_run_check_failure_on_error_ticket_starts_repair_agent`: `recorded` still contains `Check failed before this session` and now contains `.chitty/check.log`; the loop over `check line {number}\n` checks `log` instead of `recorded`, and `recorded` does not contain `check line 1\n`.
- New `test_passing_check_writes_the_log_and_ignores_it_once`, set up like `test_run_check_failure_on_todo_ticket_records_error_on_branch` but with `check = "true"` and a fake agent that only exits 0: after `self.run_cli("run")`, `log` equals `# chitty check: true\n# exit 0\n`; the exclude file (path from `git rev-parse --git-path info/exclude` in the worktree, resolved against the worktree) has exactly one line `/.chitty/`; calling `chitty.run._ignore_run_log(worktree)` again leaves exactly one.

## Acceptance Criteria

- [ ] The changed and new tests pass, and each changed or new assertion fails against the `run.py` of `main` before this change (recorded in the notes)
- [ ] `make check` passes

## History

- 2026-11-16T10:00:06Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:51Z intrepid-coral-raven backlog → planning
- 2026-11-19T17:28:38Z quick-ginger-lapwing: changed title, priority, description
- 2026-11-19T17:28:57Z quick-ginger-lapwing: changed acceptance criteria
