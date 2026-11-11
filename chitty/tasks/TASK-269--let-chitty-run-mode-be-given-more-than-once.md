---
title: Let `chitty run --mode` be given more than once
status: backlog
parent: TASK-259
created: 2026-11-11
---

## Description

- `chitty run --mode work --mode review` takes whichever job comes first in the job order across those modes. One `--mode` behaves as today; none means every mode.
- Applies to `chitty next --mode` too, and to MCP if it takes a mode.

## Acceptance Criteria

- [ ] With one `todo` and one `review` ticket, `chitty next --mode work --mode review` picks the `review` ticket, and `--mode work` alone picks the `todo` one. It fails today, because `--mode` takes one value.
- [ ] `chitty run --mode review --mode work`, with only a `todo` ticket, runs a work session (use the fake agent in `tests/test_next.py`).

## History

- 2026-11-11T13:21:05Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:42Z vivid-yellowhammer: changed acceptance criteria
