---
title: Write the runner check output to a log in the worktree, not the ticket
status: done
priority: high
created: 2026-11-16
---

## Description

The runner writes the full output of the configured `check` into ticket notes (`_run_check` and `_handle_check_failure` in `src/chitty/run.py`). A failing run puts hundreds of lines into the ticket. Decided with the owner 2026-11-19: command output never goes into tickets. It goes to a log file in the worktree, overwritten by every run, so the file always holds the last run.

Decisions:

- Module constants in `src/chitty/run.py`: `RUN_LOG = Path(".chitty/check.log")` (relative to the worktree) and `RUN_LOG_EXCLUDE = f"/{RUN_LOG.parent}/"` (`/.chitty/`).
- The log is ignored through Git's shared exclude file, not `.gitignore`, so no committed file and no `chitty init` change is needed. `git rev-parse --git-path info/exclude`, run in the worktree, names it; the output is relative in a main checkout and absolute in a linked worktree, so resolve it against the worktree. In a linked worktree it is the common Git directory's file, which every worktree reads (checked by hand 2026-11-19).
- Pure function `_with_exclude_line(text: str | None) -> str`: given the exclude file's text (`None` when it does not exist), return text that has exactly one line equal to `RUN_LOG_EXCLUDE`, keeps every other line unchanged and in order, and ends with a newline. Lines are split on `\n` only: a trailing `\n` gives no final empty line, and empty text or `None` gives no lines. When several lines equal `RUN_LOG_EXCLUDE`, keep the first and drop the rest. When none does, append it as the last line.
- `_ignore_run_log(worktree: Path) -> None` reads the exclude file (or `None`), creates its directory if missing, and writes `_with_exclude_line(...)` back only when the text changed.
- `_run_logged(phase: str, command: str, worktree: Path) -> int` runs `shlex.split(command)` first (so a malformed command raises `ValueError` before the log is touched), then calls `_ignore_run_log`, creates `worktree / ".chitty"`, opens `worktree / RUN_LOG` for writing (truncating it), writes `# chitty <phase>: <command>` and a newline, flushes, runs the split command with `cwd=worktree`, `stdin=subprocess.DEVNULL`, `env=_command_environment()`, stdout to the open file and `stderr=subprocess.STDOUT`, then, if the log does not end with a newline, writes one, then writes `# exit <returncode>` and a newline, and returns the return code. `FileNotFoundError` and `KeyboardInterrupt` are not caught there, so the log then has a header and no `# exit` line; callers keep their handling. The log is opened in binary mode (`w+b`) and the header and `# exit` lines are encoded as UTF-8, so checking the final byte never decodes command output.
- `_run_check` uses `_run_logged("check", ...)` and never captures output. Its failure detail is exactly `` check exited with status <N>; output in `.chitty/check.log` `` (backticks included), used both by `Runner error (check)` and by `Check failed before this session: ...`. The `check command not found: <command>` text is unchanged and does not mention the log.
- The log is written on success as well, so it always reflects the last run.
- Leave `_record_ticket_error` and its `Error output:` block unchanged here; `TASK-427` changes it.
- Out of scope: `setup` and the landing check (`TASK-426`).
- Docs, `docs/plan/next-action-and-runner.md`, the work-mode bullet (about lines 124 to 130): replace `note with the full output` with `` note pointing to the full output in `.chitty/check.log` ``, and replace `the ticket moves to \`error\` with the output in Notes and no agent starts.` with `` the ticket moves to `error` with a note (for a failed check, pointing to `.chitty/check.log`; for a missing command, naming it) and no agent starts. `` Nothing else in that file changes; the sentence about recording "the phase, output, and worktree" also covers setup and landing, so it stays until `TASK-426`.

Tests. `worktree` is `self.root / ".worktrees/task-1"`; `log` is `(worktree / ".chitty/check.log").read_text()`; `detail` is `` "check exited with status 1; output in `.chitty/check.log`" ``.

- Property in a new `tests/test_property_run_log_exclude.py` for `_with_exclude_line`: generate `None` or text from lists of lines (`st.text()` without newlines, `/.chitty/`, `/.chitty`, `.chitty/`, `# comment`), joined with `\n`, with and without a trailing newline. Assert: the result ends with `\n`; it has exactly one line equal to `/.chitty/`; removing that line gives the input's lines in order with any line equal to `/.chitty/` removed; applying it twice equals applying it once.
- In `tests/test_next.py`:
  - `test_run_check_failure_on_todo_ticket_records_error_on_branch`: the two `assertIn("check line 6", ...)` become `assertNotIn("check line", ...)` (task notes and `branch_ticket`). Add: `assertIn(detail, branch_ticket)`; `log` starts with `# chitty check: `, contains `check line 6\n` and ends with `# exit 1\n`; `git -C <worktree> status --short --untracked-files=all` prints exactly `?? check-args`, and `git -C <worktree> check-ignore -q .chitty/check.log` exits 0. Then overwrite the log with `old\n`, call `chitty.run._run_logged("check", tomllib.loads((self.root / "chitty.toml").read_text())["check"], worktree)`` once more, and assert `old` is absent from `log` and `check line 6\n` is present. The existing `?? check-args` assertion stays.
  - `test_run_check_failure_records_markdown_like_output`: the two `assertIn(..., notes)` become `assertNotIn("FAIL: test_something", notes)` and `assertNotIn("# not a heading", notes)`; the checker also writes `sys.stdout.write('tail without newline')` (importing `sys`) just before `raise SystemExit(1)`; `log` contains `FAIL: test_something\n`, a line that is exactly three backticks, `# not a heading\n`, and ends with `tail without newline\n# exit 1\n`.
  - `test_run_check_failure_on_doing_ticket_starts_agent` and `test_run_check_failure_on_error_ticket_starts_repair_agent`: `recorded` still contains `Check failed before this session`, now contains `detail`, and does not contain `check line`; the loop over `check line {number}\n` checks `log` instead of `recorded`.
  - New `test_passing_check_writes_the_log_and_ignores_it_once`: `self.check_project("true")`, then `self.commit_ticket("Doing", "doing")` and `self.git("branch", "task-1")`, and the same fake agent as `test_run_check_failure_on_doing_ticket_starts_agent` (it sets `status: review` and commits). After `self.run_cli("run")` prints `TASK-1: doing → review`: `log` equals `# chitty check: true\n# exit 0\n`; the exclude file (from `git rev-parse --git-path info/exclude` in the worktree, resolved against it) has exactly one line equal to `/.chitty/`; calling `chitty.run._ignore_run_log(worktree)` again leaves exactly one.
  - New `test_run_logged_keeps_output_ending_in_a_multibyte_character`: in a fresh `git init` directory, `_run_logged("check", "printf é", worktree)` returns 0 and the log is exactly `# chitty check: printf é\né\n# exit 0\n`.

## Acceptance Criteria

- [x] The property, the changed and the new tests pass. Against the `run.py` of `main` before this change, each changed failure test in `tests/test_next.py` (todo, markdown-like, doing, error) fails on the old note text (`check line` or `FAIL: test_something` found in a note, or `detail` missing). The passing-check and multibyte tests fail there because the log or `_run_logged` does not exist, and the multibyte test fails with `UnicodeDecodeError` against a text-mode `_run_logged`. Recorded in the notes
- [x] `make check` passes

## Plan

Implement the specified runner check log and shared Git exclude handling in src/chitty/run.py. Update the targeted runner tests, add the property test, and make only the named documentation sentence replacements. First run regression tests against the current behavior, then implement, format, run focused tests and make check; commit implementation in logical commits with Task: TASK-353 trailers.

## Notes

Cold read 2026-11-19 outcomes: the passing-check test needed an agent that moves to review (an unchanged agent ends in error); a truncation check; a pure `_with_exclude_line` with a property for missing files, missing final newlines and repeats; `assertNotIn("check line")` so a tail-only note fails; the exact detail string; `Error output:` left to `TASK-427`; named the doc sentences; not-found note unchanged; exclude path resolved against the worktree; `RUN_LOG_EXCLUDE` derived from `RUN_LOG`.

Second cold read 2026-11-19 outcomes: a newline before `# exit` when output lacks one, tested; exclude lines split on `\n` only, first duplicate kept; the status check is exact plus `git check-ignore`; fails-before must be on the note text; exact doc replacements; `tomllib` for the check value; `shlex.split` before the log opens; `worktree / RUN_LOG`.

Regression evidence: with `src/chitty/run.py` temporarily replaced by `main` version, `uv run python -m unittest tests.test_next.TestNext.test_run_check_failure_on_todo_ticket_records_error_on_branch` failed at the intended `assertNotIn("check line", task.section("Notes"))`; the old note contained the full checker output. Restored implementation passed the focused six-test suite. `make check` passed all 770 test suites; Ruff, pyright and formatter passed. No follow-ups.

Review failed (design): Criterion 1 requires every new or changed assertion, including the successful-check log and exclude assertions, to fail on old failure-note text. A successful check produces no failure note, so this cannot be verified as written; decide which failure-note assertions need old-version evidence and how to demonstrate the successful-check assertions. Preserve the implementation and revise the criterion before resuming. Separately, fix the newly discovered Unicode output defect below.
1: fail - With main run.py, test_passing_check_writes_the_log_and_ignores_it_once errors with FileNotFoundError for the missing log, not old note text. The markdown failure test fails on FAIL: test_something in notes; doing and error tests fail on missing detail. The earlier regression note only establishes the todo test. Also, running _run_logged with command `printf é` in a freshly initialized repository raises UnicodeDecodeError at log.read(1): seeking to the last byte splits a UTF-8 character. Check the final byte without decoding arbitrary output and add a regression test.
2: pass - `make check` exited 0: Ruff and pyright passed and 768 tests reported OK.

Planner, 2026-11-21: settled the review findings. Criterion 1 now separates the failure-note tests, which must fail on the old note text, from the two tests of new functions (`_run_logged` and the passing-check log), where failing on a missing function or log is the only possible old behaviour. Fixed the Unicode defect: the log is opened in binary mode (commit `e3604765`), with the new test `test_run_logged_keeps_output_ending_in_a_multibyte_character`. Rebased onto `main` first; the conflict in `test_run_check_failure_on_todo_ticket_records_error_on_branch` kept this branch's log assertions and `main`'s count of 2 branch commits (the claim now happens on the branch).

Fails-before evidence, each test run against `src/chitty/run.py` at the merge base `787ea874`:
- `test_run_check_failure_on_todo_ticket_records_error_on_branch`: `assertNotIn("check line", task.section("Notes"))`, check line found in the note.
- `test_run_check_failure_records_markdown_like_output`: `assertNotIn("FAIL: test_something", notes)`, found.
- `test_run_check_failure_on_doing_ticket_starts_agent` and `test_run_check_failure_on_error_ticket_starts_repair_agent`: `assertIn(detail, recorded)`, detail missing; the old note holds the full output.
- `test_passing_check_writes_the_log_and_ignores_it_once`: `FileNotFoundError` for `.chitty/check.log`.
- `test_run_logged_keeps_output_ending_in_a_multibyte_character`: `ImportError` for `_run_logged`; against the text-mode `_run_logged` (before `e3604765`) it fails with `UnicodeDecodeError`.

`make check` in the worktree: 845 tests OK, Ruff and pyright clean.

Reviewed: The earlier design and Unicode findings are resolved; the criterion now distinguishes old-note failures from missing new functionality, and the log uses binary mode.
1: pass - `make check` reported 901 tests OK, including the property and targeted tests. The planner's fails-before note records the four old-note failures, missing log and function failures, and UnicodeDecodeError against the earlier text-mode implementation.
2: pass - `make check` exited 0; Ruff and pyright passed and 901 tests reported OK.

## Summary

Worktree check logging in binary mode, shared Git exclude handling, regression and property coverage, and runner documentation. Commits `1a4ec95a` (rebased) and `e3604765`.

## History

- 2026-11-16T10:00:06Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:51Z intrepid-coral-raven backlog → planning
- 2026-11-19T17:28:38Z quick-ginger-lapwing: changed title, priority, description
- 2026-11-19T17:28:57Z quick-ginger-lapwing: changed acceptance criteria
- 2026-11-19T17:32:10Z quick-ginger-lapwing: changed description, acceptance criteria, notes
- 2026-11-19T17:34:13Z quick-ginger-lapwing: changed description, acceptance criteria, notes
- 2026-11-19T17:34:19Z quick-ginger-lapwing planning → todo
- 2026-11-19T17:35:05Z upbeat-violet-dormouse todo → doing
- 2026-11-19T17:36:49Z upbeat-violet-dormouse: wrote the plan
- 2026-11-19T17:43:43Z upbeat-violet-dormouse: changed notes, summary
- 2026-11-19T17:43:43Z upbeat-violet-dormouse doing → review
- 2026-11-19T17:47:02Z eager-hazel-crane: changed owner, acceptance criteria, notes
- 2026-11-19T17:47:02Z eager-hazel-crane review → planning
- 2026-11-21T07:56:08Z nimble-umber-gannet: changed description, acceptance criteria, notes, summary
- 2026-11-21T07:56:15Z nimble-umber-gannet: ticked acceptance criteria
- 2026-11-21T07:56:15Z nimble-umber-gannet planning → review
- 2026-11-21T08:40:52Z youthful-lilac-marten: changed notes
- 2026-11-21T08:40:52Z youthful-lilac-marten review → done
