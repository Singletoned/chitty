---
title: Stop `chitty run` reading a usage file
status: doing
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

- [ ] A `chitty run` whose fake agent prints nothing and moves the ticket to `blocked` prints no `cannot read usage file` warning, the agent environment has no `CHITTY_USAGE_FILE`, and the usage log line has no `models` key. It fails today.

## Plan

1. Add a regression test in tests/test_next.py that runs a fake agent which prints nothing and moves the ticket to blocked; assert no 'cannot read usage file' warning, no CHITTY_USAGE_FILE in the agent env, and no 'models' key in the usage line. Run it first and confirm it fails.
2. In src/chitty/run.py remove the CHITTY_USAGE_FILE set/restore, the temporary usage dir, the _read_usage call sites, and _read_usage itself; drop the 'models' key from _record_usage. Drop now-unused imports (tempfile, cast if unused).
3. Update existing tests in tests/test_next.py: fake agents stop writing CHITTY_USAGE_FILE and assert it is absent; remove the 'cannot read usage file' and USAGE_MODE invalid cases; the usage-log test drops the models expectation and is renamed to fit; delete test_usage_validation_warns_and_accepts_null_cost.
4. Update PLAN.md 'Next action and runner' usage paragraph and README.md usage log text, saying per-model totals come from scripts/pi_tokens.py.
5. Run make format and make check, commit in logical commits with 'Task: TASK-277', verify git status clean, then chitty fix and move to review with a summary.
Writers (claude-usage-hook, Pi extension) are left alone per the ticket.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-277/1`. Check it against the current criteria; do not trust it.

## History

- 2026-11-11T13:21:33Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:46Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:39:52Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:43:48Z vivid-yellowhammer: changed description, acceptance criteria, notes
- 2026-11-11T13:43:48Z vivid-yellowhammer cold-read → todo
- 2026-11-11T15:58:34Z quick-adder todo → doing
- 2026-11-11T15:58:58Z quick-adder: wrote the plan
