---
title: Stop `chitty run` reading a usage file
status: cold-read
parent: TASK-275
created: 2026-11-11
---

## Description

- `chitty run` sets `CHITTY_USAGE_FILE` and reads it after the agent exits (`_read_usage` in `src/chitty/run.py`). Only the Pi extension writes it, so without the extension every run warns `cannot read usage file`.
- Stop setting and reading it. The usage log line (`_record_usage`) keeps every field except `models`. Usage by model is gathered afterwards from session files, as a separate analysis.
- Update `PLAN.md` "Next action and runner" (the usage log paragraph) and `README.md` (usage log).

## Acceptance Criteria

- [ ] A `chitty run` with a fake agent prints no `cannot read usage file` warning, the agent environment has no `CHITTY_USAGE_FILE`, and the usage log line has no `models` key. It fails today.

## History

- 2026-11-11T13:21:33Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:46Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:39:52Z vivid-yellowhammer backlog → cold-read
