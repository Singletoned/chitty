---
title: Keep a log of each `chitty run` agent session
status: todo
depends_on:
  - TASK-278
parent: TASK-275
created: 2026-11-11
---

## Description

- In print mode an agent prints only its final message, so nobody can see what it did. `chitty run` copies the agent's stdout and stderr to a log file per session through pipes, still printing them as they arrive. Stdin stays inherited. Whole lines go to the log under one lock, in arrival order across both streams.
- Piped output is not a TTY, so an interactive agent such as the Pi TUI loses its interface. That is intended: TASK-278 moves this repository to print mode first.
- Keep the agent in the runner's process group and session (`PLAN.md` "Next action and runner"); no `start_new_session`. The readers are daemon threads joined against one shared deadline, a module constant of 2 seconds, so a descendant holding the pipe cannot keep the run alive. Detach the log before closing it; later output goes to the console only.
- `_run_agent` keeps its current signature for `tests/test_run_timeout.py`: the log is an optional keyword argument, and the `stderr=b"timed out"` sentinel survives.
- Log path: `<git common dir>/chitty/run/<ID>-<YYYYMMDDTHHMMSSffffffZ>.log`, UTC with microseconds, created exclusively (`open(..., "x")`), never committed. Create it in `_run_ticket` before `claim_edit`, so a failure to create it leaves the ticket unchanged.
- Print `log: <path>` to stderr in a `finally` around the agent run, so it appears on success, failure, timeout and interrupt.
- Pruning: at the start of every `chitty run`, with or without `--ticket`, delete `*.log` files directly in that directory whose modification time is over 30 days old. The ticket ID is the name before the final `-<stamp>.log`; skip logs whose ticket is locked (`locks.is_locked`), and keep any `.log` whose name does not match. Never touch `*.lock`. A failed delete warns on stderr.
- Test repositories need the config `chitty run` requires (`autocommit = true`, `setup`, `check`), or `run` exits before pruning.

## Acceptance Criteria

- [ ] A `chitty run` whose fake agent prints `hello` to stdout and `oops` to stderr writes a log under `<git common dir>/chitty/run/` containing both, and prints `log: <path>` on stderr. It fails today. Reuse the fake-agent pattern in `tests/test_run_timeout.py`.
- [ ] A `.log` file there with a modification time 31 days ago is deleted by the next `chitty run`; one from 29 days ago, and a `.lock` file from 31 days ago, are kept.
- [ ] When the fake agent times out, `log: <path>` is still printed, and `tests/test_run_timeout.py` passes unchanged.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-276/2`. Check it against the current criteria; do not trust it. It uses second-resolution stamps, which break `tests/test_next.py` around line 1708; the ticket now asks for microseconds.

## History

- 2026-11-11T13:21:33Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:45Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:39:51Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:41:47Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:41:55Z vivid-yellowhammer: changed dependencies
- 2026-11-11T13:41:55Z vivid-yellowhammer cold-read → planning
- 2026-11-11T13:44:12Z vivid-yellowhammer planning → cold-read
- 2026-11-11T13:51:57Z vivid-yellowhammer: changed description, notes
- 2026-11-11T13:51:57Z vivid-yellowhammer cold-read → todo
