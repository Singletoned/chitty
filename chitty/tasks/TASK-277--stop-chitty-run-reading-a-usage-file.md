---
title: Stop `chitty run` reading a usage file
status: todo
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

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-277/1`. Check it against the current criteria; do not trust it.

## History

- 2026-11-11T13:21:33Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:46Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:39:52Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:43:48Z vivid-yellowhammer: changed description, acceptance criteria, notes
- 2026-11-11T13:43:48Z vivid-yellowhammer cold-read → todo
