---
title: Write `setup` and landing-check output to the worktree log, not the ticket
status: doing
priority: high
depends_on:
  - TASK-353
created: 2026-11-19
---

## Description

Starts after `TASK-353`, which adds `_run_logged(phase: str, command: str, worktree: Path) -> int` and the constant `RUN_LOG = Path(".chitty/check.log")` to `src/chitty/run.py`. `_run_logged` truncates the log, writes `# chitty <phase>: <command>`, runs the command with stdout and stderr both into the log, writes `# exit <code>`, returns the code, and lets `FileNotFoundError` propagate. `TASK-353` uses it for the configured `check` only. `setup` (`_setup`) and the landing check (`_landing_check`) still capture their output and put it into the error, and so into the note. Decided with the owner 2026-11-19: command output never goes into tickets.

Decisions:

- `_setup` uses `_run_logged("setup", ...)` and `_landing_check` uses `_run_logged("landing check", ...)`. Both overwrite the same log, which therefore holds whichever command ran last. Landing runs `setup` and then the landing check, so after a failed landing check the log holds the landing check.
- Their errors are exactly `` setup exited with status <N>; output in `.chitty/check.log` `` and `` landing check exited with status <N>; output in `.chitty/check.log` ``. The `setup command not found: <command>` and `landing check command not found: <command>` errors and the `RunInterrupted` handling are unchanged: `_setup` and `_landing_check` catch `FileNotFoundError` from `_run_logged` as they do today.
- The `Error output:` block that `_record_ticket_error` adds is out of scope (`TASK-427`).

Tests. No property: fixed runner runs with real Git. These existing tests use substring matches that still hold and need no change: `tests/test_run_errors_on_branch.py` (`setup exited with status 1`) and `tests/test_landing.py` (`landing check exited`).

- `tests/test_run_error_reporter.py`, `test_setup_failure_handoff_preserves_full_output`: rename it `test_setup_failure_output_goes_to_the_log`. Change its setup command to `sh -c 'echo SETUP_MARKER; echo SETUP_ERR >&2; exit 9'`. Replace `assertIn("setup exited with status 9", note)` with `` assertIn("setup exited with status 9; output in `.chitty/check.log`", note) ``, and `assertIn("SETUP_MARKER", note)` with `assertNotIn`. The log, `self.root / ".worktrees/task-1/.chitty/check.log"`, starts with `# chitty setup: `, contains `SETUP_MARKER` and `SETUP_ERR`, and ends with `# exit 9\n`.
- `tests/test_review_merge.py`: in the landing-check script written in `setUp` (`landing_check.py`), add the line `"        print('LANDING_MARKER')\n"` directly before `"        raise SystemExit(7)\n"`, at the same indent inside `if Path(sys.argv[2]).exists():`. In `test_failing_check_after_main_advances_preserves_main_and_worktree`, keep the existing assertions and add: the notes contain `` landing check exited with status 7; output in `.chitty/check.log` `` and do not contain `LANDING_MARKER`; `self.worktree / ".chitty/check.log"` starts with `# chitty landing check: `, contains `LANDING_MARKER` and ends with `# exit 7\n`.
- Guards that pass before and after (no fails-before needed): in `tests/test_run_errors_on_branch.py`, a work run on the `doing` ticket from `make_doing_branch` with `setup` set on `main` to `no-such-chitty-setup-command` (as `set_setup_failure_on_main` does, but with `re.sub(r"^setup = .*$", 'setup = "no-such-chitty-setup-command"', text, flags=re.MULTILINE)`, committed on `main`) records `Runner error (setup)` and `setup command not found: no-such-chitty-setup-command` on the branch tip.

Against the `run.py` of `TASK-353`, each changed test fails; record in the notes which assertion fails first in each (expected: the note assertion, because the error still carries the output).

## Acceptance Criteria

- [ ] The changed assertions pass, and each changed test fails against the `run.py` of `TASK-353`, with the first failing assertion recorded in the notes; the command-not-found guard passes; `make check` passes

## Notes

Cold read 2026-11-19 outcomes: restated `_run_logged`; dropped the wrong `refresh_setup` claim (it runs no setup command); the landing script prints a marker and setup writes to stderr, so dropping output or stderr fails; full error strings; a command-not-found guard; rename of the setup test; listed existing tests that need no change.

Second cold read 2026-11-19 outcomes: the fails-before evidence names the first failing assertion instead of assuming `FileNotFoundError`; exact edits for the landing marker and the guard setup; `Error output:` left to `TASK-427`.

## History

- 2026-11-19T17:28:48Z quick-ginger-lapwing → planning
- 2026-11-19T17:31:27Z quick-ginger-lapwing: changed description, acceptance criteria, notes
- 2026-11-19T17:33:19Z quick-ginger-lapwing: changed description, acceptance criteria, notes
- 2026-11-19T17:34:21Z quick-ginger-lapwing planning → todo
- 2026-11-21T08:43:43Z upbeat-white-adder todo → doing
