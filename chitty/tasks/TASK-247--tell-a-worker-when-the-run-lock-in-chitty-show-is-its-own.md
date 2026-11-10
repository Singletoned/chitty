---
title: Tell a worker when the run lock in `chitty show` is its own
status: done
created: 2026-11-10
---

## Description

Workers in mullion and echonomicon read their own run lock in `chitty show` (`running: work by lively-adder, process 25131`) as a rival's, then waited for that process, their own parent, for about 20 hours.

When the lock record's `actor` equals `CHITTY_ACTOR` (which `chitty run` sets), say so. Compare with the variable, not `actor()`, which raises when no identity is set. No `actor` in the record, or `CHITTY_ACTOR` unset, means not you. Put the comparison beside `holder` in `src/chitty/locks.py`; `cli.py` and `mcp.py` both call it.

Tests: hold a lock with `run_lock(...)` inside a Git repository, as `RunLockTestCase` does. `test_show_and_list_report_the_lock_record` needs `"you": false` added.

## Acceptance Criteria

- [x] With a lock held by actor `lively-adder` and `CHITTY_ACTOR=lively-adder`, `chitty show <ID>` prints a line starting `running: you (lively-adder, work,`; with `CHITTY_ACTOR=other-name` it prints `running: work by lively-adder,` as today.
- [x] `chitty show --json` and the MCP show tool report `"you": true` or `false` inside `running` for those two cases, `false` with `CHITTY_ACTOR` unset or a pid-only lock file, and `running` is `null` with no lock.

## Plan

Add a `you` key to every record locks.holder returns: true when the record actor equals a non-empty CHITTY_ACTOR, read from the environment directly rather than actor(). cli.show renders `running: you (actor, mode, process pid, since HH:MM)` for those and the existing line otherwise; mcp.show gets the key through holder. Tests first in tests/test_run_lock.py: CLI text and --json for the four lock cases, the existing exact assertion gains "you": false, and MCP show with a held lock. Confirm they fail, then implement in locks.py and cli.py, then run make check.

## Notes

Suggestion origin: mullion

Haiku cold read 1 (`refs/cold-read/TASK-247/1`): implemented, all green; new tests failed first. Outcomes: (1) lock records without `actor` (empty or bare-pid files): fixed, the description says these are not this session. (2) `actor()` raises with no identity, which the reader handled by catching the error: fixed, compare with `CHITTY_ACTOR` directly so nothing is caught. (3) Tests need a Git repository for `run_lock`, and `CliTestCase` has none: fixed, pointed at `RunLockTestCase`. (4) An existing exact-dictionary assertion changes: fixed, named in the description. (5) MCP show had no held-lock test: no change, criterion 2 already requires one.

Verified: make format and make check pass (445 unittest suites plus Node tests); chitty fix passes with existing repository-wide Markdown warnings only. Regression tests were observed failing without the implementation in the cold read.

Reviewed: make format && make check passed (448 Python tests and Node tests). Independently exercised MCP with no lock, an unset CHITTY_ACTOR, and a pid-only lock.

1: pass - CLI displays the expected own and other actor lines.
2: pass - CLI JSON and MCP return the expected running values for each lock case.

## Summary

Implemented own-lock reporting through locks.holder for CLI and MCP JSON, and rendered the own-session marker in CLI text. Verified all acceptance criteria and full make format && make check. No follow-ups.

## History

- 2026-11-10T19:32:32Z jolly-heron → backlog
- 2026-11-10T19:32:33Z jolly-heron: changed notes
- 2026-11-10T19:32:50Z jolly-heron: changed title, description, acceptance criteria
- 2026-11-10T19:38:17Z jolly-heron: changed description, acceptance criteria
- 2026-11-10T19:38:18Z jolly-heron: changed notes
- 2026-11-10T19:38:19Z jolly-heron backlog → todo
- 2026-11-10T20:51:10Z jolly-heron: changed title, description, acceptance criteria
- 2026-11-10T21:47:36Z tidy-vole todo → doing
- 2026-11-10T21:48:19Z tidy-vole: wrote the plan
- 2026-11-10T22:19:25Z able-puffin: changed notes, summary; ticked acceptance criteria
- 2026-11-10T22:19:25Z able-puffin doing → review
- 2026-11-10T22:23:49Z nimble-jay: changed notes; ticked acceptance criteria
- 2026-11-10T22:23:49Z nimble-jay review → done
