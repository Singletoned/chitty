---
title: Time out the agent started by chitty run
status: doing
labels:
  - needs-minor
created: 2026-11-10
---

## Description

In echonomicon, a `chitty run --mode work` agent (Pi, `gpt-6-luna`) ran `while ps -p <pid of chitty run>; do sleep 5; done`, waiting on its own parent. `chitty run` waits for the agent (`subprocess.run` in `src/chitty/run.py`, around line 236), so both hung for about 20 hours with no warning.

Add an optional setting, `agent_timeout` in `chitty.toml`: a whole number of seconds. It defaults to 7200 (two hours, a module-level constant), decided with the human on 2026-11-10; `0` means no limit. A negative number or a value that is not a TOML integer (a string such as `"10"` included) is a configuration error naming the key. The default changes behaviour for every project, so this ticket carries `needs-minor`.

When the limit passes, `chitty run` stops the agent and everything it started. The configured agent command is usually a wrapper (`env ... uv run ... pi`), so killing only the direct child would leave Pi running. List the agent's descendants (for example from `ps -A -o pid= -o ppid=`), send each and the agent `SIGTERM`, then `SIGKILL` any still running after a short grace period (a module-level constant). Keep the agent in `chitty run`'s own process group and session: a cold read found that `process_group=0` stops an interactive agent reading the terminal, and `start_new_session=True` takes its controlling terminal away. Staying in the same group also leaves Ctrl-C working exactly as today. It then fails like any other agent failure: it prints `agent timed out after N seconds` and exits 1. The ticket is left as the agent left it, the usage log records the run as usual, and `--loop` stops, as it does for every agent failure (see "Next action and runner" in `PLAN.md`).

Out of scope: an idle or no-output limit (the agent writes straight to the terminal, so `chitty run` sees no output to time), moving on to the next ticket after a timeout, and a guide line telling agents not to wait on their parent. Update the "Next action and runner" section of `PLAN.md` and the configuration docs.

## Acceptance Criteria

- [ ] With `agent_timeout = 2` and an agent command that starts a child process which sleeps for 60 seconds, `chitty run` exits 1 within 10 seconds, prints `agent timed out after 2 seconds`, neither process is still running afterwards, and the usage log has an entry for the run.
- [ ] With `agent_timeout = 0`, an agent that sleeps for 3 seconds finishes normally; `agent_timeout = -5` or `"10"` fails with a configuration error naming `agent_timeout`; and with no `agent_timeout` set, the limit is the default constant, which is 7200, and a test that patches that constant to 2 sees `agent timed out after 2 seconds`.
- [ ] The agent runs in the same process group as `chitty run` (the fake agent records `os.getpgid(0)`), so terminal input and Ctrl-C reach it as today.

## Plan

Add strict agent_timeout configuration with a 7200-second module constant and zero disabling; enforce deadline in run.py, terminate descendants then agent with TERM and KILL after a grace period without changing process group/session; add regression tests for timeout, descendant cleanup, usage logging, validation, default, and process group; update PLAN.md and configuration docs.

## Notes

Suggestion origin: echonomicon

Haiku cold read 1 (`refs/cold-read/TASK-246/1`): implemented as written, all green; new tests failed first. Outcomes: (1) `process_group=0` breaks interactive terminal input, and `start_new_session` drops the controlling terminal: fixed, now kills the descendant tree and keeps the agent in the same group, which replaced the Ctrl-C criterion. (2) The "longer than any test limit" bound was untestable: fixed, now 3 seconds. (3) `"10"` needs strict integer parsing: fixed, the description says a string is an error. (4) Usage log after a timeout was untested: fixed, added to criterion 1. (5) Reader skipped the `PLAN.md` and docs updates: no change, the description already asks for them.

## History

- 2026-11-10T16:53:45Z jolly-heron → backlog
- 2026-11-10T16:53:45Z jolly-heron: changed notes
- 2026-11-10T16:54:04Z jolly-heron: changed description, acceptance criteria
- 2026-11-10T16:54:04Z jolly-heron backlog → todo
- 2026-11-10T16:54:11Z jolly-heron todo → backlog
- 2026-11-10T16:59:38Z jolly-heron: changed description, acceptance criteria
- 2026-11-10T16:59:40Z jolly-heron: changed notes
- 2026-11-10T17:34:39Z jolly-heron: changed labels, description, acceptance criteria
- 2026-11-10T17:34:48Z jolly-heron: changed acceptance criteria
- 2026-11-10T17:34:48Z jolly-heron backlog → todo
- 2026-11-10T17:35:46Z brisk-yellowhammer todo → doing
- 2026-11-10T17:35:55Z brisk-yellowhammer: wrote the plan
