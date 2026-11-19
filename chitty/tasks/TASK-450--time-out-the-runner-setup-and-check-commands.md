---
title: Time out the runner `setup` and `check` commands
status: backlog
created: 2026-11-19
---

## Description

On 2026-11-19 the `chitty run --mode review` check for `TASK-428` ran `make check` for over 27 minutes and would never have finished: one `unittest-parallel` worker deadlocked on its own `flock` (`.git/chitty/run/main-checkout.lock` open twice in one process, from branch `task-428`), and the other workers sat idle. `_run_check`, `_setup` and `_landing_check` in `src/chitty/run.py` call `subprocess.run` with no timeout, so a hung command blocks the loop with no error and no ticket note. Agent sessions already have `agent_timeout` (`DEFAULT_AGENT_TIMEOUT = 7200` in `src/chitty/config.py`). Proposal: a `command_timeout` setting, in seconds and defaulting to a generous fixed value, applied to `setup`, `check` and the landing check. When it expires, kill the process group and record it like any other failure of that phase, for example `check timed out after N seconds`.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:24Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:25Z sunny-white-dormouse: changed notes
