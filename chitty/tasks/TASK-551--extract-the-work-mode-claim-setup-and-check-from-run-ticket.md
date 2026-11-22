---
title: Extract the work-mode claim, setup and check from `_run_ticket_with_log`
status: todo
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-540` on 2026-11-22. `_run_ticket_with_log` in `src/chitty/run.py` is about 225 lines; `TASK-552` needs to skip its work-mode `setup` and `check` steps when a rebase is left stopped. This ticket is a behaviour-preserving extraction first, so that change is one condition.

Move the work-mode `todo` claim, `setup` and the `_run_check` block (today: the `if action.mode == "work" and selected_status == "todo":` claim, the `if action.mode == "work":` setup block, and the `if failed := _run_check(...)` block) into a helper `_prepare_work_session(...) -> RunResult | None` that returns the `RunResult` the caller should return early, or `None` to carry on. Keep the order and every message the same. Review mode is untouched.

No new tests: the existing runner tests (`tests/test_next.py`, `tests/test_run_*.py`, `tests/test_review_merge.py`, `tests/test_run_claims_on_branch.py`, `tests/test_run_work_rebases.py`) cover this code and must pass unchanged. Draft: check the exact current lines on `main` before starting, as `TASK-540` lands first.

## Acceptance Criteria

- [ ] The helper exists and `_run_ticket_with_log` calls it; every existing runner test passes unchanged; `make check` passes

## Notes

Dependency on `TASK-540` removed 2026-11-22: its code is on `main` (commit `9027093c`); only its ticket status awaits a person.

## History

- 2026-11-22T03:43:00Z lively-zinc-newt → todo
- 2026-11-22T04:23:46Z lively-zinc-newt: changed dependencies, notes
