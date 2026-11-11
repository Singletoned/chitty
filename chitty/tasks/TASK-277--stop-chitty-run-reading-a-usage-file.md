---
title: Stop `chitty run` reading a usage file
status: review
parent: TASK-275
created: 2026-11-11
---

## Description

- `chitty run` sets `CHITTY_USAGE_FILE` and reads it after the agent exits (`_read_usage` in `src/chitty/run.py`). Only the Pi extension and the hidden `claude-usage-hook` write it, so without the extension every run warns `cannot read usage file`.
- Stop setting and reading it. The usage log line (`_record_usage`) keeps every field except `models`. Usage by model is gathered afterwards from session files (`scripts/pi_tokens.py`).
- Update the tests that depend on the usage file in `tests/test_next.py`: the fake agents' `CHITTY_USAGE_FILE` writes, the `cannot read usage file` assertions, the `models` assertions, and the `_read_usage` validation test. Rename tests whose names no longer fit.
- Update `PLAN.md` "Next action and runner" (the usage log paragraph) and `README.md` (usage log), pointing to `scripts/pi_tokens.py`.
- Out of scope: deleting the writers. `claude-usage-hook` goes in TASK-281; the Pi writer goes with the extension in TASK-279.

## Acceptance Criteria

- [x] A `chitty run` whose fake agent prints nothing and moves the ticket to `blocked` prints no `cannot read usage file` warning, the agent environment has no `CHITTY_USAGE_FILE`, and the usage log line has no `models` key. It fails today.

## Plan

1. Add a regression test in tests/test_next.py that runs a fake agent which prints nothing and moves the ticket to blocked; assert no 'cannot read usage file' warning, no CHITTY_USAGE_FILE in the agent env, and no 'models' key in the usage line. Run it first and confirm it fails.
2. In src/chitty/run.py remove the CHITTY_USAGE_FILE set/restore, the temporary usage dir, the _read_usage call sites, and _read_usage itself; drop the 'models' key from _record_usage. Drop now-unused imports (tempfile, cast if unused).
3. Update existing tests in tests/test_next.py: fake agents stop writing CHITTY_USAGE_FILE and assert it is absent; remove the 'cannot read usage file' and USAGE_MODE invalid cases; the usage-log test drops the models expectation and is renamed to fit; delete test_usage_validation_warns_and_accepts_null_cost.
4. Update PLAN.md 'Next action and runner' usage paragraph and README.md usage log text, saying per-model totals come from scripts/pi_tokens.py.
5. Run make format and make check, commit in logical commits with 'Task: TASK-277', verify git status clean, then chitty fix and move to review with a summary.
Writers (claude-usage-hook, Pi extension) are left alone per the ticket.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-277/1`. Check it against the current criteria; do not trust it.

Regression test: test_run_without_usage_file_is_silent_and_logs_no_models in tests/test_next.py. Run before the fix it failed with warning: cannot read usage file ... file is missing. After the fix it passes.

Decision (cheap to reverse): _command_environment now also drops an inherited CHITTY_USAGE_FILE. The shell that ran the tests exported it, so the agent inherited it and the criterion failed. Remove that pop if you would rather not strip it.

Consequence for review: because the variable is no longer set or stripped for agents, the Pi extension and claude-usage-hook write nothing during chitty run until TASK-279 and TASK-281 remove them.

Tests: test_run_cases expected one record for the removed invalid-usage run, so it now expects four doing rows. test_usage_validation_warns_and_accepts_null_cost was deleted because it covered the removed _read_usage. Kept the name test_run_records_usage_outside_repository_and_appends_runs; it still fits.

## Summary

Handoff: chitty run no longer sets, reads or records CHITTY_USAGE_FILE. The usage log line has no models key. _read_usage is removed. PLAN.md and README.md now point to scripts/pi_tokens.py for spend by model. Two commits: 15257b0 (code and tests) and 12059c7 (docs).

Verification: make format and make check pass (ruff, pyright 0 errors, 488 unittest suites, Node tests). The new regression test failed before the fix and passes after it.

Follow-ups: TASK-279 and TASK-281 remove the Pi writer and claude-usage-hook. chitty fix printed Markdown delimiter warnings for archived tickets; those are not from this change and were left alone.

## History

- 2026-11-11T13:21:33Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:46Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:39:52Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:43:48Z vivid-yellowhammer: changed description, acceptance criteria, notes
- 2026-11-11T13:43:48Z vivid-yellowhammer cold-read → todo
- 2026-11-11T15:58:34Z quick-adder todo → doing
- 2026-11-11T15:58:58Z quick-adder: wrote the plan
- 2026-11-11T16:04:39Z quick-adder: changed notes, summary; ticked acceptance criteria
- 2026-11-11T16:04:39Z quick-adder doing → review
