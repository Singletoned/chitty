---
title: Time out the agent started by chitty run
status: todo
created: 2026-11-10
---

## Description

In echonomicon, a `chitty run --mode work` agent (Pi, `gpt-6-luna`) ran `while ps -p <pid of chitty run>; do sleep 5; done`, waiting on its own parent. `chitty run` waits for the agent (`subprocess.run` in `src/chitty/run.py`, around line 236), so both hung for about 20 hours with no warning.

Add an optional setting, `agent_timeout` in `chitty.toml`: a whole number of seconds, greater than zero. Unset means no limit, as today. A value that is not a positive integer is a configuration error naming the key.

When the limit passes, `chitty run` stops the agent and everything it started: run the agent in its own process group and send that group `SIGTERM`, then `SIGKILL` after a short grace period (a module-level constant). The configured agent command is usually a wrapper (`env ... uv run ... pi`), so killing only the direct child would leave Pi running. It then fails like any other agent failure: it prints `agent timed out after N seconds` and exits 1. The ticket is left as the agent left it, the usage log records the run as usual, and `--loop` stops, as it does for every agent failure (see "Next action and runner" in `PLAN.md`).

Ctrl-C must still stop the agent and `chitty run` with exit 130, as it does today. A separate process group does not receive the terminal's `SIGINT`, so `chitty run` has to pass it on.

Out of scope: an idle or no-output limit (the agent writes straight to the terminal, so `chitty run` sees no output to time), moving on to the next ticket after a timeout, and a guide line telling agents not to wait on their parent. Update the "Next action and runner" section of `PLAN.md` and the configuration docs.

## Acceptance Criteria

- [ ] With `agent_timeout = 2` and an agent command that starts a child process which sleeps for 60 seconds, `chitty run` exits 1 within 10 seconds, prints `agent timed out after 2 seconds`, and neither process is still running afterwards.
- [ ] Without `agent_timeout`, an agent that runs longer than any test limit is not stopped; and `agent_timeout = 0`, `-5` or `"10"` fails with a configuration error naming `agent_timeout`.
- [ ] Sending `SIGINT` to `chitty run` while a timed agent runs stops the agent and its child, and `chitty run` exits 130.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-10T16:53:45Z jolly-heron → backlog
- 2026-11-10T16:53:45Z jolly-heron: changed notes
- 2026-11-10T16:54:04Z jolly-heron: changed description, acceptance criteria
- 2026-11-10T16:54:04Z jolly-heron backlog → todo
