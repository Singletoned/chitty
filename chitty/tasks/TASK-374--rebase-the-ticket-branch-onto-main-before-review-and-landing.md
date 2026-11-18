---
title: Rebase the ticket branch onto `main` before review and landing
status: planning
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

Starts after `TASK-359` lands: `merge_ticket` and `TicketMergeConflict` do not exist yet.

Decisions:

- Pure function `ticket_only_conflicts(conflicts: Sequence[tuple[str, Path]], ticket_directories: Sequence[Path]) -> bool` in `src/chitty/git.py`, over `(status code, path)` pairs from `git status --porcelain`: true exactly when the list is non-empty and every entry has code `UU` and a path whose parent is exactly one of the directories. Any other unmerged code (`AA`, `AU`, `UA`, `DU`, `UD`, `DD`), a nested path, or a sibling directory sharing a prefix (`tasks-old` beside `tasks`) makes it false.
- Build `git.rebase_onto(root: Path, main_branch: str, ticket_directories: Sequence[Path]) -> list[str]` here; `TASK-370` reuses it. `ticket_directories` are the active and archive directories of every configured context, relative to the repository. It runs `git -c rerere.enabled=false rebase --autostash <main_branch>`. At each stop where `ticket_only_conflicts` holds, it resolves each path with `merge_ticket` (`TASK-359`) from index stages 1, 2 and 3, writes and stages it, and continues with `git -c core.editor=true rebase --continue`, as many times as the rebase stops. It returns `[]` when the rebase completes. Otherwise, it leaves the rebase stopped and returns every unmerged path, ticket files included; a `TicketMergeConflict` makes its path count as unmerged. A Git failure that is not a conflict raises `ChittyError`.
- `_prepare_review` calls it instead of `merge_main`. On a returned conflict it runs `git rebase --abort` and fails the review as `Review failed (integration)` naming every path in backticks, as today. `TASK-375` later replaces that with a conflict-resolution session.
- `_land` calls it too, instead of `git.merge`, then fast-forwards `main`. A conflict aborts the rebase and is a landing error, as today. Remove `git.merge` and `git.merge_main`; nothing else uses them.
- Ctrl-C during either rebase aborts it, exit 130: `_prepare_review` keeps its `KeyboardInterrupt` handler, and `_land` gains one that aborts the rebase and raises `RunInterrupted("landing")`. No test: it needs a signal mid-rebase.
- The uncommitted-files block before a review stays.
- In `docs/plan/next-action-and-runner.md`, add the principle paragraph, and say under `## Before a review` (step 4) and `## Landing` that the branch is rebased onto `main` and ticket-file conflicts are merged mechanically.

Tests: a Hypothesis property for `ticket_only_conflicts` in a new `tests/test_property_ticket_conflicts.py`: generate directory lists and conflict lists mixing every unmerged code with paths directly in a directory, nested below one, in a prefix-sharing sibling, and elsewhere; the result is true exactly when the list is non-empty and every entry qualifies, whatever the order. Create the function first raising `NotImplementedError`. Real-Git, fake-agent runner tests in `tests/test_review_merge.py` and `tests/test_landing.py`, using `GIT_COMMITTER_DATE` where order matters, as `tests/test_store.py` does; the fake reviewer writes a marker file when it starts. The runner paths have no property: real Git and runner processes over the fixed cases in the criteria.

## Acceptance Criteria

- [ ] The `ticket_only_conflicts` property in `tests/test_property_ticket_conflicts.py` passes and fails against the `NotImplementedError` stub
- [ ] A review run where `main` has a new commit to a file the branch does not touch: `git rev-list --merges main..<branch>` is empty, `main` is an ancestor of the branch, and the fake reviewer records one start
- [ ] A review run where `main` and the branch both appended different notes to the ticket, the branch in two separate commits so the rebase stops twice, and the same for a ticket in an archive directory (a context with `archive = "move"`): the rebase completes with every note kept, no rebase is in progress, and the fake reviewer records one start without the `latest committed version` error; the test fails before the change
- [ ] A review run whose rebase stops with both a ticket-file conflict and a code conflict (both sides changed the same lines of one source file): no rebase is in progress, the ticket is `doing`, its note contains `Review failed (integration)` and both paths in backticks, and no reviewer starts
- [ ] A landing after a non-conflicting commit on `main` fast-forwards `main` to the rebased branch with no merge commit; `git.merge` and `git.merge_main` are gone; `docs/plan/next-action-and-runner.md` has the principle and the rebase under both headings; `make check` passes

## Notes

On hold 2026-11-18: the ticket state model is being redesigned (the ticket branch is authoritative for its ticket while it exists; no runner writes on `main` for in-flight tickets). See `docs/plan/ticket-state.md` on branch `plan/ticket-state`. Re-plan against that before working.

## History

- 2026-11-18T09:51:20Z witty-ginger-falcon → planning
- 2026-11-18T09:52:34Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:56:01Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:56:03Z witty-ginger-falcon: changed description, acceptance criteria
- 2026-11-18T09:56:05Z witty-ginger-falcon planning → todo
- 2026-11-18T15:47:46Z witty-ginger-falcon: changed notes
- 2026-11-18T15:47:46Z witty-ginger-falcon todo → planning
