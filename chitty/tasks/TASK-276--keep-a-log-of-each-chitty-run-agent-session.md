---
title: Keep a log of each `chitty run` agent session
status: planning
parent: TASK-275
created: 2026-11-11
---

## Description

In print mode an agent prints only its final message, and `chitty run` captures agent output only to put it into an error. When a session goes wrong nobody can see what the agent did: on 2026-11-14 in circuitry and 2026-11-19 in echonomicon, tickets went to `error` as `was unchanged` after agents that exited 0 in about two seconds, and nothing recorded why (`TASK-441`, `TASK-443`). This ticket keeps a log of each ticket run and shows agent output live. Pruning old logs is `TASK-465`; naming the log in error notes is `TASK-466`.

Decisions (2026-11-19; an earlier partial implementation on branch `task-276` was deleted, start from `main`):

- One log per ticket run, covering every continuation session (`_agent_sessions` in `src/chitty/run.py` may call `_run_session` up to `MAX_CONTINUATIONS` more times). Path: `<git common dir>/chitty/run/<ID>-<YYYYMMDDTHHMMSSffffffZ>.log`, UTC with microseconds, `<ID>` as in `TASK-12`. Never committed (it is inside the Git directory).
- `_run_ticket` creates it with `open(path, "x", encoding="utf-8")` before `claim_edit`, so a failure to create it leaves the ticket unchanged; `FileExistsError` is not retried: raise `ChittyError` naming the path. `_run_ticket` owns the file: it passes it down to `_run_session` (a new required parameter `log: TextIO`), and in a `finally` around the agent phase closes it and prints `log: <path>` to stderr, so the line appears on success, failure, timeout and interrupt.
- `_run_agent(command, *, cwd, env, timeout, log)` gains a required keyword argument `log: TextIO | None` (no default value). Agent stdout and stderr stay merged into one pipe, as today (`stderr=subprocess.STDOUT`), so arrival order and whole lines need no extra work. One daemon reader thread reads the pipe line by line and, for each line, writes it to `sys.stderr` and to `log` (when not `None`), and keeps it for the returned `CompletedProcess.stdout` exactly as today. So `chitty run`'s stdout keeps only its status lines, and notes keep the agent output they hold today.
- After the agent exits (or is stopped on timeout), `_run_agent` joins the reader against one deadline, the module constant `AGENT_OUTPUT_GRACE_SECONDS = 2`, so a descendant that keeps the pipe open cannot keep the run alive. Before returning it detaches the log under a lock, so the reader never writes to it again; any later output goes to stderr only. A reader thread must never raise (a review on 2026-11-14 saw `ValueError: write to closed file` from such a thread).
- Keep the timeout handling and the `stderr=b"timed out"` sentinel as they are. Keep the agent in the runner's process group and session; no `start_new_session` (`docs/plan/next-action-and-runner.md`).
- In `tests/test_run_timeout.py` the only change is adding `log=None` to its direct `_run_agent` calls.
- Document the log and the stderr echo in `docs/plan/next-action-and-runner.md` and `README.md`, where they describe `chitty run` output.

Tests: no property. This is real process and pipe handling, and its parts (an agent, its descendants, a deadline) cannot be pulled into a pure function. Reuse the fake-agent pattern in `tests/test_run_timeout.py`; put new tests in a new `tests/test_run_agent_log.py`.

## Acceptance Criteria

- [ ] A `chitty run` whose fake agent prints `hello` to stdout and `oops` to stderr, then sets the ticket to `review` and commits, writes one log under `<git common dir>/chitty/run/` containing both lines; the runner's stderr contains `hello`, `oops` and `log: <that path>`; its stdout is exactly the status line. It fails today.
- [ ] A direct `_run_agent` call with a log, whose agent starts a descendant that prints `LATE` after 2.5 seconds and then exits at once, returns in under 2.5 seconds; no thread raises (`threading.excepthook` replaced to record calls records none); `LATE` is not in the log. It fails today (the call waits for the descendant).
- [ ] When the fake agent times out, `log: <path>` is still printed and that log contains the agent output; `tests/test_run_timeout.py` passes with only `log=None` added to its direct calls.
- [ ] With the run log directory made read-only before `chitty run`, the run exits non-zero with an error naming the log path, and the ticket file and `git log` are unchanged. `make check` passes.

## Notes

Planner, 2026-11-19: rewritten from scratch. The earlier implementation on branch `task-276` (tip `e26f0cd5`) was deleted at the owner's request because it had gone stale and conflicted with `main`; ignore any `refs/cold-read/TASK-276/*` refs. Its 2026-11-14 review failed on a conflict between streaming output to the console and the unchanged timeout test, resolved here by echoing agent output to stderr. Split out: pruning (`TASK-465`) and log paths in error notes (`TASK-466`).

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
- 2026-11-19T21:18:33Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:18:33Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:18:51Z sunny-white-dormouse: replaced notes
