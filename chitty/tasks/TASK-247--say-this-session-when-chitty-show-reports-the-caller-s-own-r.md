---
title: Say "this session" when `chitty show` reports the caller's own run lock
status: backlog
created: 2026-11-10
---

## Description

In mullion (TASK-2, 2026-11-09), a `chitty run --mode work` agent (model `gpt-6-luna`) ran `chitty show TASK-2` and saw `running: work by lively-adder, process 25131, since 20:43`. That was its own `chitty run`, but nothing said so. It took the line for a rival worker, left the files alone, and ran `while ps -p 25131 >/dev/null; do sleep 5; done`, which waits on its own parent forever. The ticket sat in `doing` for about 20 hours. The same thing happened in echonomicon (see TASK-246, the timeout backstop). This ticket fixes the cause.

`chitty run` already gives the agent its actor name in `CHITTY_ACTOR` (`src/chitty/run.py`, around line 83), and the lock record holds the same name under `actor` (`_running_line` in `src/chitty/cli.py`). When the lock's actor equals the current actor (`actor()` in `src/chitty/actor.py`), `chitty show` prints `running: this session (work by lively-adder, process 25131, since 20:43)` instead. Otherwise the line is unchanged. The JSON from `chitty show --json` and the MCP show tool (`src/chitty/mcp.py`, around line 152) gain `"this_session": true` or `false` inside `running` when a lock is held, and `running` stays `null` when none is. Put the comparison in one function outside `cli.py` and `mcp.py` that both call.

Out of scope: TASK-234 (telling agents to leave a locked ticket alone), and Pi not enforcing its bash tool `timeout`, which the suggestion also raises.

## Acceptance Criteria

- [ ] With a lock held for a ticket by actor `lively-adder` and `CHITTY_ACTOR=lively-adder`, `chitty show <ID>` prints a line starting `running: this session (work by lively-adder,`; with `CHITTY_ACTOR=other-name` it prints `running: work by lively-adder,` as today.
- [ ] In the same two cases, `chitty show --json` and the MCP show tool report `"this_session": true` and `false` inside `running`; with no lock, `running` is `null`.

## Notes

Suggestion origin: mullion

## History

- 2026-11-10T19:32:32Z jolly-heron → backlog
- 2026-11-10T19:32:33Z jolly-heron: changed notes
- 2026-11-10T19:32:50Z jolly-heron: changed title, description, acceptance criteria
