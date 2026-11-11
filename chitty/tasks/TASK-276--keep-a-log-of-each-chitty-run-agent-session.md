---
title: Keep a log of each `chitty run` agent session
status: cold-read
depends_on:
  - TASK-278
parent: TASK-275
created: 2026-11-11
---

## Description

- In print mode an agent prints only its final message, so nobody can see what it did. `chitty run` copies the agent's stdout and stderr to a log file per session through pipes, still printing them as they arrive. Stdin stays inherited.
- Piped output is not a TTY, so an interactive agent such as the Pi TUI loses its interface. That is intended: TASK-278 moves this repository to print mode first.
- Keep the agent in the runner's process group and session (`PLAN.md` "Next action and runner"); no `start_new_session`. The readers must not keep the run alive after the agent exits, even if a descendant still holds the pipe: use daemon threads with a bounded join.
- Log path: `<git common dir>/chitty/run/<ID>-<YYYYMMDDTHHMMSSZ>.log`, UTC, created exclusively (`open(..., "x")`), never committed. If it cannot be created, fail before the agent starts.
- Print `log: <path>` to stderr in a `finally` around the agent run, so it appears on success, failure, timeout and interrupt.
- Pruning: in `run()` in `src/chitty/run.py`, before `_land_pending`, delete `*.log` files directly in that directory whose modification time is over 30 days old, skipping logs whose ticket is locked (`locks.is_locked`). Never touch `*.lock`. A failed delete warns on stderr. `--loop` starts a fresh `chitty run` per attempt, so this runs per attempt.

## Acceptance Criteria

- [ ] A `chitty run` whose fake agent prints `hello` to stdout and `oops` to stderr writes a log under `<git common dir>/chitty/run/` containing both, and prints `log: <path>` on stderr. It fails today. Reuse the fake-agent pattern in `tests/test_run_timeout.py`.
- [ ] A `.log` file there with a modification time 31 days ago is deleted by the next `chitty run`; one from 29 days ago, and a `.lock` file from 31 days ago, are kept.
- [ ] When the fake agent times out, `log: <path>` is still printed, and `tests/test_run_timeout.py` passes unchanged.

## History

- 2026-11-11T13:21:33Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:45Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:39:51Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:41:47Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:41:55Z vivid-yellowhammer: changed dependencies
- 2026-11-11T13:41:55Z vivid-yellowhammer cold-read → planning
- 2026-11-11T13:44:12Z vivid-yellowhammer planning → cold-read
