---
title: Tell a worker when the run lock in `chitty show` is its own
status: todo
created: 2026-11-10
---

## Description

Workers in mullion and echonomicon read their own run lock in `chitty show` (`running: work by lively-adder, process 25131`) as a rival's, then waited for that process, their own parent, for about 20 hours.

When the lock record's `actor` equals `CHITTY_ACTOR` (which `chitty run` sets), say so. Compare with the variable, not `actor()`, which raises when no identity is set. No `actor` in the record, or `CHITTY_ACTOR` unset, means not you. Put the comparison beside `holder` in `src/chitty/locks.py`; `cli.py` and `mcp.py` both call it.

Tests: hold a lock with `run_lock(...)` inside a Git repository, as `RunLockTestCase` does. `test_show_and_list_report_the_lock_record` needs `"you": false` added.

## Acceptance Criteria

- [ ] With a lock held by actor `lively-adder` and `CHITTY_ACTOR=lively-adder`, `chitty show <ID>` prints a line starting `running: you (lively-adder, work,`; with `CHITTY_ACTOR=other-name` it prints `running: work by lively-adder,` as today.
- [ ] `chitty show --json` and the MCP show tool report `"you": true` or `false` inside `running` for those two cases, `false` with `CHITTY_ACTOR` unset or a pid-only lock file, and `running` is `null` with no lock.

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
- 2026-11-10T20:51:10Z jolly-heron: changed title, description, acceptance criteria
