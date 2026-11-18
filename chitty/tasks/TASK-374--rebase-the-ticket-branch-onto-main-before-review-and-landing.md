---
title: Rebase the ticket branch onto `main` before review and landing
status: cold-read
labels:
  - bug
  - needs-minor
priority: high
depends_on:
  - TASK-359
created: 2026-11-18
---

## Description

Today `_prepare_review` merges `main` into the ticket branch with `git.merge_main`, and `_land` merges it again with `git.merge` before fast-forwarding `main` (`src/chitty/run.py`). A conflict only in the ticket file fails the review and, writing that failure from the worktree, can stop `chitty run --loop` with `<ID>'s latest committed version is on branch main` (`TASK-333` 2026-11-16, `TASK-364` 2026-11-17).

Principle (decided 2026-11-18): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it; this is mechanical. Ticket files are merged mechanically too, because the branch's ticket commits carry the worker's progress. Only code conflicts go to an agent.

Decisions:

- New `git.rebase_onto(root: Path, main_branch: str, ticket_directories: Sequence[Path]) -> list[str]` in `src/chitty/git.py`, shared with `TASK-370` (build it here if this ticket lands first). It runs `git -c rerere.enabled=false rebase --autostash <main_branch>`. At each stop where every unmerged path is a `UU` file directly in one of `ticket_directories` (the configured active and archive directories), it resolves each with `merge_ticket` (`TASK-359`) from index stages 1, 2 and 3, stages it, and continues with `git -c core.editor=true rebase --continue`. It returns `[]` when the rebase completes, and otherwise leaves the rebase stopped and returns the unmerged paths. A `TicketMergeConflict` counts as an unmerged path. A Git failure that is not a conflict raises `ChittyError`.
- `_prepare_review` calls it instead of `merge_main`. On a code conflict it runs `git rebase --abort` and fails the review as `Review failed (integration)` naming the files, as today. `TASK-375` later replaces that with a conflict-resolution session.
- `_land` calls it too, instead of `git.merge`, then fast-forwards `main`. A conflict aborts the rebase and is a landing error, as today. Remove `git.merge` and `git.merge_main` when nothing uses them.
- The uncommitted-files block before a review stays.
- Ctrl-C during the rebase aborts it, exit 130.
- Update "Before a review" and "Landing" in `docs/plan/next-action-and-runner.md`, and add the principle above.

Tests: real-Git, fake-agent runner tests in `tests/test_review_merge.py` and `tests/test_landing.py`, using `GIT_COMMITTER_DATE` where order matters, as `tests/test_store.py` does. No property: real Git and runner processes over the fixed cases in the criteria; the pure decision is `merge_ticket`'s.

## Acceptance Criteria

- [ ] A review run where `main` has a new non-conflicting commit leaves the branch as `main` plus the branch's own commits with no merge commit, and starts the reviewer
- [ ] A review run where `main` and the branch both appended a note to the ticket completes the rebase, keeps both notes, and starts the reviewer without the `latest committed version` error; the test fails before the change
- [ ] A review run with a code conflict leaves no rebase in progress and moves the ticket to `doing` with `Review failed (integration)` naming the file
- [ ] A landing after `main` moved on lands with `main` fast-forwarded to the rebased branch and no merge commit
- [ ] `docs/plan/next-action-and-runner.md` states the principle and the rebase, and `make check` passes

## History

- 2026-11-18T09:51:20Z witty-ginger-falcon → planning
- 2026-11-18T09:52:34Z witty-ginger-falcon planning → cold-read
