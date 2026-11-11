---
title: Stop `chitty run` reading a usage file
status: backlog
parent: TASK-275
created: 2026-11-11
---

## Description

- `chitty run` sets `CHITTY_USAGE_FILE` and reads it after the agent exits (`_read_usage` and `_record_usage` in `src/chitty/run.py`); without the Pi extension nothing writes it, so every run warns `cannot read usage file`.
- Remove the usage file and the usage records. Usage is gathered afterwards from session files, as a separate analysis.

## History

- 2026-11-11T13:21:33Z vivid-yellowhammer → backlog
