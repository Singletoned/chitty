---
title: Let `chitty run --mode` be given more than once
status: todo
parent: TASK-259
created: 2026-11-11
---

## Description

- `chitty run --mode work --mode review` takes whichever job comes first in the job order across those modes. One `--mode` behaves as today; none means every mode. `--mode` with `--ticket` stays refused.
- Applies to `chitty next --mode` too. MCP `next` takes no mode, so it is unchanged.
- With several modes and nothing to pick, print `no next ticket for --mode review or work`.
- `--loop` passes every `--mode` on to each new run.

## Acceptance Criteria

- [ ] With one `todo` and one `review` ticket, `chitty next --mode review --mode work` picks the `review` ticket; today it picks the `todo` one, because only the last `--mode` counts. `--mode work` alone picks the `todo` one.
- [ ] `chitty run --mode review --mode work`, with only a `todo` ticket, runs a work session (use the fake agent in `tests/test_next.py`). This guards the new code; it passes today.
- [ ] `chitty run --loop --mode review --mode work` passes both `--mode` options to each run it starts.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-269/1`. Check it against the current criteria; do not trust it. It does not test `--loop` forwarding.

## History

- 2026-11-11T13:21:05Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:42Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T13:39:49Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:44:29Z vivid-yellowhammer: changed description, acceptance criteria, notes
- 2026-11-11T13:44:29Z vivid-yellowhammer cold-read → todo
- 2026-11-11T13:44:35Z vivid-yellowhammer: changed acceptance criteria
