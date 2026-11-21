---
title: Check linked-worktree ticket reads against every branch placement
status: planning
depends_on:
  - TASK-393
created: 2026-11-21
---

## Description

`TASK-393` adds the placement builder `tests/ticket_placements.py` (`make_repo`, `PLACEMENTS`, `place`, `edit_uncommitted`) and checks every placement read from the main checkout. This ticket checks the same placements read from linked worktrees, which is where `current_branch` matters in `Repo._choose_source` (`src/chitty/store.py`).

Starts after `TASK-393` lands; it extends that module and test file, so compare with what landed before working. Out of scope: more than one ticket, random dates, decoy branches (`TASK-<generated>`), provisional tickets.

Builder addition in `tests/ticket_placements.py`: `checkout(root, kind, number) -> Path` returns the directory to read from, adding linked worktrees under `<root>/.worktrees/` with `git worktree add`:

- (2) the ticket's own worktree on `task-<n>`, only for placements with a local branch: (b), (d), (e), (g), (h), (j), (k), (l);
- (3) another ticket's worktree: commit `TASK-<n+1>` (title `other`) on its own branch `task-<n+1>` and add its worktree;
- (4) a worktree on new branch `feature`, made from `main`'s tip after every `main` commit;
- (5) a worktree with a detached `HEAD` at `main`.

Expected results, by hand in the module (never by calling `ticket_source`):

- kinds (3), (4), (5): the same as the main checkout in `TASK-393`, except (i), which is not listed (the uncommitted file is only in the main checkout), and except that an uncommitted edit never shows.
- kind (2): (b), (g) the worktree's working tree, which is the branch content plus any uncommitted edit; (h) not listed; (d), (l) `remote`; (e) and (k) raise as in `TASK-393`; (j) `main-2`, and an uncommitted edit in the worktree does not show.

The planner must confirm each expected result against `main` with a probe before the cold read, as was done for `TASK-393`.

Tests in `tests/test_property_ticket_reads.py`:

- `test_linked_worktree_placements`: for every compatible (placement, kind) pair, read with `Repo.open(<checkout>)`: `find(TASK-5)` and `tasks(context("tasks"), "all")`, as `TASK-393` does. Where the ticket's file exists in that checkout's working tree, repeat in a fresh repository with `edit_uncommitted` applied there. Use `subTest`.
- A mutant test that passes `Repo._main_branch()` as `current_branch` (patch `chitty.store.ticket_source` as in `tests/test_source_copy_checkouts.py`) and asserts that at least one check fails.

No property: one ticket, fixed placements and checkout kinds, each listed and tested.

## Acceptance Criteria

- [ ] `test_linked_worktree_placements` passes, covering every compatible (placement, checkout kind) pair, with and without an uncommitted edit where the file exists
- [ ] The `current_branch` mutant test passes, showing at least one check fails under the mutant; `make check` passes

## Notes

Split from `TASK-393` on 2026-11-21. Keep in planning until `TASK-393` lands; then compare with the landed builder, probe the expected results, cold-read and move to `todo`.

## History

- 2026-11-21T23:05:23Z lively-zinc-newt → planning
- 2026-11-21T23:06:00Z lively-zinc-newt: changed notes
