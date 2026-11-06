---
title: Let `chitty run` fail a review before it starts, despite verdict lines
status: doing
priority: high
owner: human
created: 2026-11-06
---

## Description

`_validate_review_verdict` in `src/chitty/store.py` (added by `TASK-166`, `0022e1e`) requires a `N: pass|fail - reason` line for every criterion on any `review → doing` or `review → done` edit. `_fail_review` in `src/chitty/run.py` moves a ticket `review → doing` with only a `Review failed (work)` or `Review failed (integration)` note, when the worktree is dirty or the rebase onto `main` conflicts. That edit is now refused (`review verdict lines must match ...; missing 1`), `chitty run --mode review` exits 1, and the review loop stops on the same ticket every time. Seen on `TASK-173`, whose branch conflicts with `main`.

The existing `_fail_review` tests in `tests/test_review_rebase.py` still pass, because their tickets have no criteria and `_validate_review_verdict` returns early when there are none. The new tests need a ticket with a criterion. `branch_for_review` doesn't add one, so add it in the test with `chitty edit 1 --ac ...` before branching (autocommit is on).

Decision: these failures happen before any criterion is reviewed, so there's nothing to give a verdict on. `_fail_review` passes `Edit(..., skip_verdicts=True)`. That's a new internal field on the `Edit` dataclass, not exposed in the CLI or MCP, and `Repo.edit` skips `_validate_review_verdict` when it is set. Nothing else changes: the failure still counts towards the failed-review limit and still needs a note. No `__version__` bump, because nothing `chitty init` writes changes.

Out of scope: the Pi extension's `spawn chitty ENOENT` after a reviewer removes its own worktree.

## Acceptance Criteria

- [ ] A test in `tests/` runs `chitty run --mode review` on a ticket with one criterion whose branch conflicts with `main`. It asserts that the ticket moves to `doing` with the `Review failed (integration)` note, and that the run exits 0. It fails before the fix with `review verdict lines must match`.
- [ ] The same holds for the uncommitted-changes case (`Review failed (work)`). A new test asserts that a manual `chitty edit ID -s doing --note ...` on a review ticket with a criterion and no verdict lines still fails with `review verdict lines must match`.

## Plan

Add an internal `skip_verdicts` field to the `Edit` dataclass. `Repo.edit` skips `_validate_review_verdict` when it is set, and `_fail_review` sets it. Tests in `tests/test_review_rebase.py`: a conflict and a dirty worktree on a ticket with one criterion (`chitty run` exits 0 and moves the ticket to `doing`), and a manual `edit -s doing` without verdicts still refused.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-206/1`; the two run tests failed before and passed after; `make check` OK). Outcomes:
- Why the existing tests miss the bug (tickets with no criteria): fixed, the ticket now explains it.
- `branch_for_review` has no criteria support: fixed, the ticket says to add one with `chitty edit 1 --ac`.
- Criterion 2 relied on existing tests for the manual guard, but none exist: fixed, it now requires a new test.
- `Edit` is a frozen dataclass: confirmed it fits, and the ticket now says so.
- Exit 1 before and 0 after: confirmed.
- No version bump: confirmed, and the ticket now says so.
- `make format` before `make check`: rejected, `AGENTS.md` already says it.

Reserved for a human-run session so the loops leave it alone.

## History

- 2026-11-06T12:03:13Z youthful-toad → backlog
- 2026-11-06T12:11:11Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T12:11:11Z youthful-toad backlog → todo
- 2026-11-06T12:20:03Z youthful-toad: changed owner, notes
- 2026-11-06T12:20:06Z youthful-toad: wrote the plan
- 2026-11-06T12:20:06Z youthful-toad todo → doing
