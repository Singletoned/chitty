---
title: Keep a log of each `chitty run` agent session
status: cold-read
parent: TASK-275
created: 2026-11-11
---

## Description

- In print mode an agent prints only its final message, so nobody can see what it did. `chitty run` copies the agent's stdout and stderr to a log file per session through pipes, and also writes them to the runner's stderr as they arrive (decided 2026-11-19): `chitty run`'s stdout keeps only its status lines, so `tests/test_run_timeout.py` and other exact stdout assertions stay valid. Stdin stays inherited. Whole lines go to the log under one lock, in arrival order across both streams.
- Piped output is not a TTY, so an interactive agent such as the Pi TUI loses its interface. That is intended: TASK-278 moves this repository to print mode first.
- Keep the agent in the runner's process group and session (`docs/plan/next-action-and-runner.md`); no `start_new_session`. The readers are daemon threads joined against one shared deadline, a module constant of 2 seconds, so a descendant holding the pipe cannot keep the run alive. Detach the log before closing it; later output goes to the console only.
- `_run_agent` keeps its current signature for `tests/test_run_timeout.py`: the log is an optional keyword argument, and the `stderr=b"timed out"` sentinel survives.
- Log path: `<git common dir>/chitty/run/<ID>-<YYYYMMDDTHHMMSSffffffZ>.log`, UTC with microseconds, created exclusively (`open(..., "x")`), never committed. Create it in `_run_ticket` before `claim_edit`, so a failure to create it leaves the ticket unchanged.
- Print `log: <path>` to stderr in a `finally` around the agent run, so it appears on success, failure, timeout and interrupt.
- Every agent-phase runner error names the log, so the ticket note says where to look: `_run_session`'s `agent timed out after N seconds` and `agent exited with status N` errors, and `_agent_sessions`'s `<ID> was unchanged; ...` error (`src/chitty/run.py`), each end with a new line `log: <path>`. Seen 2026-11-14 in circuitry and 2026-11-19 in echonomicon: tickets went to `error` as `was unchanged` after agents that exited 0 in about two seconds, and nothing recorded why (`TASK-441`, `TASK-443`).
- A reader thread must never write to a closed log: detach the log under the lock before closing it, so output from a descendant that outlives the agent goes to stderr only.
- Pruning: at the start of every `chitty run`, with or without `--ticket`, delete `*.log` files directly in that directory whose modification time is over 30 days old. The ticket ID is the name before the final `-<stamp>.log`; skip logs whose ticket is locked (`locks.is_locked`), and keep any `.log` whose name does not match. Never touch `*.lock`. A failed delete warns on stderr.
- Test repositories need the config `chitty run` requires (`autocommit = true`, `setup`, `check`), or `run` exits before pruning.

## Acceptance Criteria

- [ ] A `chitty run` whose fake agent prints `hello` to stdout and `oops` to stderr writes a log under `<git common dir>/chitty/run/` containing both, and prints `log: <path>` on stderr. It fails today. Reuse the fake-agent pattern in `tests/test_run_timeout.py`.
- [ ] A `.log` file there with a modification time 31 days ago is deleted by the next `chitty run`; one from 29 days ago, and a `.lock` file from 31 days ago, are kept.
- [ ] When the fake agent times out, `log: <path>` is still printed, and `tests/test_run_timeout.py` passes unchanged.
- [ ] A `chitty run` whose fake `{mode} {id}` agent prints `NOTHING_DONE` to stderr and exits 0 without committing moves the ticket to `error`; its note contains `was unchanged` and `log: <path>`, and that log contains `NOTHING_DONE`. It fails today.
- [ ] A direct `_run_agent` call with a log, whose agent starts a descendant that prints after 2.5 seconds and then exits at once, returns, closes the log, and raises no exception in any thread (`threading.excepthook` records none); the late line is not in the log.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-276/2`. Check it against the current criteria; do not trust it. It uses second-resolution stamps, which break `tests/test_next.py` around line 1708; the ticket now asks for microseconds.

Planner, 2026-11-14: removed the dependency on TASK-278. Its only prerequisite for this ticket, print-mode Pi as `agent_command`, is already on `main` (`c2eae4b`); TASK-278 waits only on human trial runs.

Planner, 2026-11-19: the earlier partial implementation on branch `task-276` (tip `e26f0cd5`) was deleted at the owner's request: it had gone stale and conflicted with `main`. Start again from `main`. Its review (2026-11-14) failed on a conflict between streaming agent output to the console and the unchanged timeout test; resolved below by streaming to stderr. That review also found a `ValueError: write to closed file` from a reader thread when a descendant printed after the log closed: detach the log before closing it, and test late output.

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
- 2026-11-12T21:35:00Z kind-yellow-vole: changed description
- 2026-11-14T09:20:55Z jolly-silver-falcon: changed dependencies, notes
- 2026-11-19T21:12:12Z sunny-white-dormouse: changed notes
- 2026-11-19T21:12:12Z sunny-white-dormouse todo → planning
- 2026-11-19T21:12:26Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:12:39Z sunny-white-dormouse planning → cold-read
