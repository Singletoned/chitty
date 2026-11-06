---
title: Show which tickets `chitty run` is working on
status: backlog
priority: medium
depends_on:
  - TASK-72
created: 2026-11-06
---

## Description

Nothing tells a person which tickets a `chitty run` is working on right now, or who is working on them. Each run holds an exclusive `flock` on `<git common dir>/chitty/run/<ID>.lock` (`src/chitty/locks.py`, `TASK-200`), but that file holds only the process ID. Reading it means a script.

1. **Lock record.** `run_lock` writes one JSON object to the lock file instead of the bare PID: `{"pid": ..., "actor": ..., "mode": "work"|"review", "started": "<ISO 8601 UTC>"}`.
   - `actor` is the run's `CHITTY_ACTOR`. Today `run` in `src/chitty/run.py` assigns it in `_run_ticket`, after `_lock_ticket` takes the lock. Move that assignment before `_lock_ticket` so the record has it.
   - Add `locks.holder(root, task_id) -> dict | None`, which returns the record while the lock is held and `None` otherwise. Content that isn't valid JSON (a lock held by an older Chitty) gives `{"pid": <the text>}`.
   - The `TicketLocked` message keeps naming the PID.
2. **`chitty show`.** A held ticket gets a line after the frontmatter block: `running: review by <actor>, process <pid>, since <HH:MM>` (local time). `show --json` and the MCP `show` tool in `src/chitty/mcp.py` add a `running` field, the record or `null`. Add it in those two commands only, not in `StoredTask.as_dict`, which `add` and `edit` also use.
3. **`chitty list`.** `TASK-72` adds `skip_reason`, the text `chitty next` gives for skipping a ticket. Give a held ticket the reason `▶ running`, checked first, because `next_action` skips held tickets before any other rule. Nothing else about the run goes in `list`; `show` has the detail.

Update the run-lock paragraph in `README.md` and the "Next action and runner" section of `PLAN.md`.

Out of scope:
- Loops idle between runs, which hold no lock.
- Runs on other machines.

## Acceptance Criteria

- [ ] `chitty show ID` on a ticket whose run lock is held prints `running: <mode> by <actor>, process <pid>, since <HH:MM>`, and `show --json` and the MCP `show` tool give the record in `running`; with no lock held there is no line and `running` is `null`. Tests hold the lock through `locks.run_lock`, and one writes a bare PID to show the older-format fallback.
- [ ] A test runs `chitty run` with a fake agent that captures `chitty show` output and the lock file while it runs: the record's `actor` equals the agent's `CHITTY_ACTOR`, and `mode` matches the run.
- [ ] `chitty list` ends a held ticket's row with `▶ running` (through `skip_reason`), and `README.md` and `PLAN.md` describe the record, the `show` line and the marker.

## History

- 2026-11-06T12:45:12Z youthful-toad → backlog
