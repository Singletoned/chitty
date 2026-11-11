---
title: Mark the start and end of each `chitty run --loop` attempt
status: doing
created: 2026-11-11
---

## Description

- Watching `chitty run --loop`, it is hard to see where one run ends and the wait begins. `run_loop` in `src/chitty/run.py` starts each attempt as a child process and sleeps `RUN_LOOP_PAUSE_SECONDS` between them.
- Before each attempt, `run_loop` prints a full-width rule, `━━━━ chitty run · 16:04:12 ━━━…`. After it, another: `━━━━ finished · next run at 16:05:12 ━━━…`, or `━━━━ no ticket · next run at …` when there was nothing to do, or `━━━━ stopped · exit 2 ━━━…` when the loop ends. The width is the terminal's (`shutil.get_terminal_size`), and times are local.
- Rules go to stderr, with the existing `no next ticket` line. Ctrl-C needs no rule. Only the loop prints these; a single `chitty run` is unchanged.

## Acceptance Criteria

- [ ] A test runs `run_loop` with a child that exits 0 once and then non-zero: the output has a start rule before each attempt, a `finished · next run at` rule after the first, and a `stopped · exit` rule after the second. It fails today.
- [ ] A child exiting `NO_NEXT_TICKET_EXIT` (3) is followed by a `no ticket · next run at` rule, not `finished`.
- [ ] The `next run at` time is `RUN_LOOP_PAUSE_SECONDS` after the end of that attempt, not its start.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-287/1`. Check it against the current criteria; do not trust it.

## History

- 2026-11-11T16:09:29Z vivid-yellowhammer → backlog
- 2026-11-11T16:09:36Z vivid-yellowhammer: changed parent
- 2026-11-11T16:09:48Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T16:12:20Z vivid-yellowhammer: changed description
- 2026-11-11T16:12:21Z vivid-yellowhammer: changed acceptance criteria, notes
- 2026-11-11T16:12:21Z vivid-yellowhammer cold-read → todo
- 2026-11-11T21:41:08Z jolly-amber-yellowhammer todo → doing
