---
title: Let `chitty run` fail a review before it starts, despite verdict lines
status: backlog
priority: high
created: 2026-11-06
---

## Description

`_validate_review_verdict` in `src/chitty/store.py` (added by `TASK-166`, `0022e1e`) requires a `N: pass|fail - reason` line for every criterion on any `review → doing` or `review → done` edit. `_fail_review` in `src/chitty/run.py` moves a ticket `review → doing` with only a `Review failed (work)` or `Review failed (integration)` note, when the worktree is dirty or the rebase onto `main` conflicts. That edit is now refused (`review verdict lines must match ...; missing 1`), `chitty run --mode review` exits 1, and the review loop stops on the same ticket every time. Seen on `TASK-173`, whose branch conflicts with `main`.

Decision: these failures happen before any criterion is reviewed, so there's nothing to give a verdict on. `_fail_review` passes `Edit(..., skip_verdicts=True)` (a new internal `Edit` field, not exposed in the CLI or MCP), and `Repo.edit` skips `_validate_review_verdict` when it is set. Everything else is unchanged: the failure still counts towards the failed-review limit, and still needs a note.

Out of scope: the Pi extension's `spawn chitty ENOENT` after a reviewer removes its own worktree.

## Acceptance Criteria

- [ ] A test in `tests/` runs `chitty run --mode review` on a ticket with one criterion whose branch conflicts with `main`. It asserts that the ticket moves to `doing` with the `Review failed (integration)` note, and that the run exits 0. It fails before the fix with `review verdict lines must match`.
- [ ] The same holds for the uncommitted-changes case (`Review failed (work)`), and `chitty edit ID -s doing --note ...` on a review ticket still requires verdict lines (existing tests pass).

## History

- 2026-11-06T12:03:13Z youthful-toad → backlog
