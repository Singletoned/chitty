---
title: Write the runner check output to a log in the worktree, not the ticket
status: planning
priority: high
created: 2026-11-16
---

## Description

The runner writes the full output of the configured `check` into ticket notes (`_run_check` and `_handle_check_failure` in `src/chitty/run.py`). A failing run puts hundreds of lines into the ticket. Decided with the owner 2026-11-19: command output never goes into tickets. It goes to a log file in the worktree, overwritten by every run, so the file always holds the last run.

Decisions:

- Module constants in `src/chitty/run.py`: `RUN_LOG = Path(".chitty/check.log")` (relative to the worktree) and `RUN_LOG_EXCLUDE = f"/{RUN_LOG.parent}/"` (`/.chitty/`).
- The log is ignored through Git's shared exclude file, not `.gitignore`, so no committed file and no `chitty init` change is needed. `git rev-parse --git-path info/exclude`, run in the worktree, names it; the output is relative in a main checkout and absolute in a linked worktree, so resolve it against the worktree. In a linked worktree it is the common Git directory's file, which every worktree reads (checked by hand 2026-11-19).
- Pure function `_with_exclude_line(text: str | None) -> str`: given the exclude file's text (`None` when it does not exist), return text that has exactly one line equal to `RUN_LOG_EXCLUDE`, keeps every other line unchanged and in order, and ends with a newline. When no line equals it already, add a newline first if `text` is non-empty and lacks one, then append the line.
- `_ignore_run_log(worktree: Path) -> None` reads the exclude file (or `None`), creates its directory if missing, and writes `_with_exclude_line(...)` back only when the text changed.
- `_run_logged(phase: str, command: str, worktree: Path) -> int` calls `_ignore_run_log`, creates `.chitty/`, opens `RUN_LOG` for writing (truncating it), writes `# chitty <phase>: <command>` and a newline, flushes, runs `shlex.split(command)` with `cwd=worktree`, `stdin=subprocess.DEVNULL`, `env=_command_environment()`, stdout to the open file and `stderr=subprocess.STDOUT`, then writes `# exit <returncode>` and a newline and returns the return code. `FileNotFoundError` and `KeyboardInterrupt` are not caught there, so the log then has a header and no `# exit` line; callers keep their handling.
- `_run_check` uses `_run_logged("check", ...)` and never captures output. Its failure detail is exactly `` check exited with status <N>; output in `.chitty/check.log` `` (backticks included), used both by `Runner error (check)` and by `Check failed before this session: ...`. The `check command not found: <command>` text is unchanged and does not mention the log.
- The log is written on success as well, so it always reflects the last run.
- Leave `_record_ticket_error` and its `Error output:` block unchanged here; `TASK-427` changes it.
- Out of scope: `setup` and the landing check (`TASK-426`).
- Docs: in `docs/plan/next-action-and-runner.md`, change only the two check sentences that say the output goes into the note ("with the full output" and "with the output in Notes", about lines 127 to 131) to say it goes to `.chitty/check.log`. The sentence about recording "the phase, output, and worktree" also covers setup and landing, so it stays until `TASK-426`.

Tests. `worktree` is `self.root / ".worktrees/task-1"`; `log` is `(worktree / ".chitty/check.log").read_text()`; `detail` is `` "check exited with status 1; output in `.chitty/check.log`" ``.

- Property in a new `tests/test_property_run_log_exclude.py` for `_with_exclude_line`: generate `None` or text from lists of lines (`st.text()` without newlines, `/.chitty/`, `/.chitty`, `.chitty/`, `# comment`), joined with `\n`, with and without a trailing newline. Assert: the result ends with `\n`; it has exactly one line equal to `/.chitty/`; removing that line gives the input's lines in order with any line equal to `/.chitty/` removed; applying it twice equals applying it once.
- In `tests/test_next.py`:
  - `test_run_check_failure_on_todo_ticket_records_error_on_branch`: the two `assertIn("check line 6", ...)` become `assertNotIn("check line", ...)` (task notes and `branch_ticket`). Add: `assertIn(detail, branch_ticket)`; `log` starts with `# chitty check: `, contains `check line 6\n` and ends with `# exit 1\n`; the output of `git -C <worktree> status --short --untracked-files=all` does not contain `.chitty`. Then overwrite the log with `old\n`, call `chitty.run._run_logged("check", the `check` value from this test's `chitty.toml`, worktree)` once more, and assert `old` is absent from `log` and `check line 6\n` is present. The existing `?? check-args` assertion stays.
  - `test_run_check_failure_records_markdown_like_output`: the two `assertIn(..., notes)` become `assertNotIn("FAIL: test_something", notes)` and `assertNotIn("# not a heading", notes)`; `log` contains `FAIL: test_something\n`, a line that is exactly three backticks, and `# not a heading\n`.
  - `test_run_check_failure_on_doing_ticket_starts_agent` and `test_run_check_failure_on_error_ticket_starts_repair_agent`: `recorded` still contains `Check failed before this session`, now contains `detail`, and does not contain `check line`; the loop over `check line {number}\n` checks `log` instead of `recorded`.
  - New `test_passing_check_writes_the_log_and_ignores_it_once`: `self.check_project("true")`, then `self.commit_ticket("Doing", "doing")` and `self.git("branch", "task-1")`, and the same fake agent as `test_run_check_failure_on_doing_ticket_starts_agent` (it sets `status: review` and commits). After `self.run_cli("run")` prints `TASK-1: doing → review`: `log` equals `# chitty check: true\n# exit 0\n`; the exclude file (from `git rev-parse --git-path info/exclude` in the worktree, resolved against it) has exactly one line equal to `/.chitty/`; calling `chitty.run._ignore_run_log(worktree)` again leaves exactly one.

## Acceptance Criteria

- [ ] The property, the changed and the new tests pass, and each changed or new assertion in `tests/test_next.py` fails against the `run.py` of `main` before this change (recorded in the notes)
- [ ] `make check` passes

## Notes

Cold read 2026-11-19 outcomes: the passing-check test needed an agent that moves to review (an unchanged agent ends in error); a truncation check; a pure `_with_exclude_line` with a property for missing files, missing final newlines and repeats; `assertNotIn("check line")` so a tail-only note fails; the exact detail string; `Error output:` left to `TASK-427`; named the doc sentences; not-found note unchanged; exclude path resolved against the worktree; `RUN_LOG_EXCLUDE` derived from `RUN_LOG`.

## History

- 2026-11-16T10:00:06Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:51Z intrepid-coral-raven backlog → planning
- 2026-11-19T17:28:38Z quick-ginger-lapwing: changed title, priority, description
- 2026-11-19T17:28:57Z quick-ginger-lapwing: changed acceptance criteria
- 2026-11-19T17:32:10Z quick-ginger-lapwing: changed description, acceptance criteria, notes
