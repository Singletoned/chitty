---
title: Summarise recorded test timings and outcomes for the retro
status: backlog
depends_on:
  - TASK-591
created: 2026-11-22
---

## Description

Planner, 2026-11-22: a script (for example `scripts/test_timings.py`) reading `.git/chitty/test-timings.jsonl` (`TASK-590`, `TASK-591`): slowest tests by median and their trend, and tests that both passed and failed at the same commit (evidence of a flaky test or a real intermittent bug). Make the summary a pure function with properties. Add a step to the retro in `docs/plan/pipeline-and-feedback.md` to read it and decide on moving slow tests out of `make check`.

## History

- 2026-11-22T17:16:34Z plucky-umber-wren → backlog
