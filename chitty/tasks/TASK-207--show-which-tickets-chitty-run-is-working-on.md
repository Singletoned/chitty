---
title: Show which tickets `chitty run` is working on
status: doing
priority: medium
depends_on:
  - TASK-72
created: 2026-11-06
---

## Description

Nothing tells a person which tickets a `chitty run` is working on right now, or who is working on them. Each run holds an exclusive `flock` on `<git common dir>/chitty/run/<ID>.lock` (`src/chitty/locks.py`, `TASK-200`), but that file holds only the process ID. Reading it means a script.

1. **Lock record.** `run_lock(root, task_id, *, actor, mode)` has required keyword arguments, so update its existing callers, including the tests and their `HOLDER` script. It writes one JSON object instead of the bare PID: `{"pid": ..., "actor": ..., "mode": "work"|"review", "started": "<ISO 8601 UTC>"}`.
   - `actor` is the run's `CHITTY_ACTOR`. Today `run` in `src/chitty/run.py` assigns it in `_run_ticket`, after `_lock_ticket` takes the lock. Move the assignment to the start of `run`, straight after the argument refusals.
   - `mode` is `action.mode`, which `_lock_ticket` passes when it takes the lock, after choosing the ticket.
   - Add `locks.holder(root, task_id) -> dict | None`, which returns the record while the lock is held and `None` otherwise. A plain read works even while this process holds the lock, because `flock` is advisory.
   - Content that isn't valid JSON (a lock from an older Chitty) gives `{"pid": <the text>}`. Empty content, a brief window between `ftruncate` and `write`, gives `{"pid": "unknown"}`.
   - The `TicketLocked` message keeps naming the PID.
2. **`chitty show`.** For a held ticket, the last line of the output, after `worked on:` and `children:`, is `running: review by <actor>, process <pid>, since <HH:MM>` (local time). A record without `actor` (older format) prints `running: process <pid>`.
   - `show --json` and the MCP `show` tool in `src/chitty/mcp.py` add a `running` field, the record or `null`. Add it in those two commands only, not in `StoredTask.as_dict`, which `add` and `edit` also use.
   - Three existing tests compare `show` JSON with `add`, `note` or `renumber` JSON: `test_same_json_as_cli` in `tests/test_mcp.py` and `test_mcp_tool_matches_the_cli_json` in `tests/test_renumber.py`. Make them compare without `running`.
3. **`chitty list`.** `TASK-72` adds `skip_reason(repo, stored)`. Its first check is the run lock (`locks.is_locked`), giving `▶ running`, because `next_action` skips held tickets before any other rule. `next_action` may keep its own up-front filter. Only `todo`, `doing` and `review` tickets can be held, which are the statuses `skip_reason` covers. Nothing else about the run goes in `list`; `show` has the detail.

Update the run-lock paragraph in `README.md` and the "Next action and runner" section of `PLAN.md`.

Out of scope:
- Loops idle between runs, which hold no lock.
- Runs on other machines.

## Acceptance Criteria

- [ ] `chitty show ID` on a ticket whose run lock is held prints `running: <mode> by <actor>, process <pid>, since <HH:MM>`, and `show --json` and the MCP `show` tool give the record in `running`; with no lock held there is no line and `running` is `null`. Tests hold the lock through `locks.run_lock`, and one writes a bare PID to show the older-format fallback.
- [ ] `chitty list` ends a held ticket's row with `▶ running` (through `skip_reason`), and `README.md` and `PLAN.md` describe the record, the `show` line and the marker.
- [ ] A test runs `chitty run` with a fake agent that runs `chitty show --json` in a child process (`python -c "from chitty.cli import cli; cli()"`) and saves the output while it runs. The saved `running` record's `actor` equals the agent's `CHITTY_ACTOR`, and its `mode` matches the run.

## Plan

Implement lock records and holder parsing in locks.py, thread actor/mode through run_lock callers, and expose runtime details in show/list and MCP without changing StoredTask serialization. Add regression coverage including an in-process held lock, legacy/empty records, list marker, and a fake-agent child-process run. Update README.md and the relevant PLAN.md section. Run the targeted tests first where a new regression test can demonstrate the unfixed behavior, then format and make check.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-207/1`; implemented items 1 and 2; tests failed first; `make check` OK). Outcomes:
- Three existing `show`-versus-`add`/`renumber` JSON tests break: fixed, the ticket names them.
- `run_lock` signature not given: fixed, required keyword arguments `actor` and `mode`, and callers are updated.
- Where the actor assignment goes: fixed, directly before `with ExitStack()`.
- The mode is only known after choosing: fixed, `_lock_ticket` passes `action.mode`.
- Empty-file race: fixed, it shows as `unknown`. An atomic write is rejected as unnecessary for a display.
- Older-format display: fixed, `running: process <pid>`.
- `show` line placement was ambiguous: fixed, it's the last line.
- `skip_reason` must check the lock itself: fixed, the ticket now says so.
- How the fake agent reads `show`: fixed, in a child process.
- Leftover `CHITTY_ACTOR` after `TicketLocked` or `NoNextTicket`: rejected, each run sets its own.

Depends on `TASK-210`, which moves the run's actor assignment to the start of `run`. That replaces this ticket's own instruction to move it after the inbox pull, which would have kept the `cannot determine actor` bug.

No longer depends on `TASK-210`, which now removes the inbox pull from `chitty run` instead of moving the actor assignment. This ticket moves the assignment itself, to the start of `run`.

## History

- 2026-11-06T12:45:12Z youthful-toad → backlog
- 2026-11-06T13:05:30Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T13:05:30Z youthful-toad backlog → todo
- 2026-11-06T13:44:20Z youthful-toad: changed dependencies, description, notes
- 2026-11-06T13:45:26Z youthful-toad: changed dependencies, description, notes
- 2026-11-06T20:31:25Z plucky-vole todo → doing
- 2026-11-06T20:31:53Z plucky-vole: wrote the plan
