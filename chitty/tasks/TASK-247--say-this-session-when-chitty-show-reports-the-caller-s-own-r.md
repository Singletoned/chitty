---
title: Say "this session" when `chitty show` reports the caller's own run lock
status: todo
created: 2026-11-10
---

## Description

In mullion (TASK-2, 2026-11-09), a `chitty run --mode work` agent (model `gpt-6-luna`) ran `chitty show TASK-2` and saw `running: work by lively-adder, process 25131, since 20:43`. That was its own `chitty run`, but nothing said so. It took the line for a rival worker, left the files alone, and ran `while ps -p 25131 >/dev/null; do sleep 5; done`, which waits on its own parent forever. The ticket sat in `doing` for about 20 hours. The same thing happened in echonomicon (see TASK-246, the timeout backstop). This ticket fixes the cause.

`chitty run` already gives the agent its actor name in `CHITTY_ACTOR` (`src/chitty/run.py`, around line 83), and the lock record holds the same name under `actor` (`_running_line` in `src/chitty/cli.py`). When the lock record's `actor` equals the `CHITTY_ACTOR` environment variable, `chitty show` prints `running: this session (work by lively-adder, process 25131, since 20:43)` instead. Otherwise the line is unchanged. The JSON from `chitty show --json` and the MCP show tool (`src/chitty/mcp.py`, around line 152) gain `"this_session": true` or `false` inside `running` when a lock is held, and `running` stays `null` when none is. Compare with `CHITTY_ACTOR` itself, not `actor()`: `chitty run` sets it, and `actor()` raises when no identity is set, which would make `show` fail. It is not this session when `CHITTY_ACTOR` is unset or empty, or when the record has no `actor` (`locks.holder` returns just a `pid` for an empty or non-JSON lock file). Put the comparison in one function outside `cli.py` and `mcp.py` that both call, for example beside `holder` in `src/chitty/locks.py`. Tests can hold a lock in-process with `run_lock(root, ticket, actor=..., mode=...)` inside a Git repository, as `RunLockTestCase` in `tests/test_run_lock.py` does; `CliTestCase` creates no repository. `test_show_and_list_report_the_lock_record` compares `running` with an exact dictionary and will need `"this_session": false` added.

Out of scope: TASK-234 (telling agents to leave a locked ticket alone), and Pi not enforcing its bash tool `timeout`, which the suggestion also raises.

## Acceptance Criteria

- [ ] With a lock held for a ticket by actor `lively-adder` and `CHITTY_ACTOR=lively-adder`, `chitty show <ID>` prints a line starting `running: this session (work by lively-adder,`; with `CHITTY_ACTOR=other-name` it prints `running: work by lively-adder,` as today.
- [ ] In the same two cases, `chitty show --json` and the MCP show tool report `"this_session": true` and `false` inside `running`; with `CHITTY_ACTOR` unset, or a lock file holding only a pid, they report `false` and `show` succeeds; with no lock, `running` is `null`.

## Notes

Suggestion origin: mullion

Haiku cold read 1 (`refs/cold-read/TASK-247/1`): implemented, all green; new tests failed first. Outcomes: (1) lock records without `actor` (empty or bare-pid files): fixed, the description says these are not this session. (2) `actor()` raises with no identity, which the reader handled by catching the error: fixed, compare with `CHITTY_ACTOR` directly so nothing is caught. (3) Tests need a Git repository for `run_lock`, and `CliTestCase` has none: fixed, pointed at `RunLockTestCase`. (4) An existing exact-dictionary assertion changes: fixed, named in the description. (5) MCP show had no held-lock test: no change, criterion 2 already requires one.

## History

- 2026-11-10T19:32:32Z jolly-heron → backlog
- 2026-11-10T19:32:33Z jolly-heron: changed notes
- 2026-11-10T19:32:50Z jolly-heron: changed title, description, acceptance criteria
- 2026-11-10T19:38:17Z jolly-heron: changed description, acceptance criteria
- 2026-11-10T19:38:18Z jolly-heron: changed notes
- 2026-11-10T19:38:19Z jolly-heron backlog → todo
