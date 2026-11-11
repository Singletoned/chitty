---
title: Mark the start and end of each `chitty run --loop` attempt
status: backlog
created: 2026-11-11
---

## Description

- Watching `chitty run --loop`, it is hard to see where one run ends and the wait begins. `run_loop` in `src/chitty/run.py` starts each attempt as a child process and sleeps `RUN_LOOP_PAUSE_SECONDS` between them.
- Before each attempt, `run_loop` prints a full-width rule, `━━━━ chitty run · 16:04:12 ━━━…`. After it, another: `━━━━ finished · next run at 16:05:12 ━━━…`, or `━━━━ no ticket · next run at …` when there was nothing to do, or `━━━━ stopped · exit 2 ━━━…` when the loop ends. The width is the terminal's (`shutil.get_terminal_size`), and times are local.
- Only the loop prints these; a single `chitty run` is unchanged.

## Acceptance Criteria

- [ ] A test runs `run_loop` with a child that exits 0 once and then non-zero: the output has a start rule before each attempt, a `finished · next run at` rule after the first, and a `stopped · exit` rule after the second. It fails today.

## History

- 2026-11-11T16:09:29Z vivid-yellowhammer → backlog
- 2026-11-11T16:09:36Z vivid-yellowhammer: changed parent
