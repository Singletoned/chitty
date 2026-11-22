---
title: Check linked-worktree ticket reads against every branch placement
status: cold-read
depends_on:
  - TASK-527
created: 2026-11-21
---

## Description

`TASK-393` and `TASK-527` landed `tests/ticket_placements.py` (`PLACEMENTS` = `a` to `m`, `Expected`, `git`, `make_repo`, `write_ticket`, `edit_uncommitted`, `commit`, `place`) and `test_main_checkout_placements` in `tests/test_ticket_placement_reads.py`, which reads every placement from the main checkout. This ticket reads the same placements from three kinds of linked worktree that are not the ticket's own; the ticket's own worktree is `TASK-537`. Rechecked on `main` 2026-11-22.

Builder addition in `tests/ticket_placements.py`: `checkout(root: Path, kind: int, number: int) -> Path`, returning the directory to read from:

- kind 3, another ticket's worktree: on a new branch `task-<number+1>` from `main`, `write_ticket(root, number + 1, "other")` and `commit(root, 20)`, switch back to `main`, then `git worktree add .worktrees/task-<number+1> task-<number+1>`;
- kind 4: `git worktree add -b feature .worktrees/feature main`;
- kind 5: `git worktree add --detach .worktrees/detached main`.

Expected results, read with `Repo.open(<checkout>)`: in all three kinds, the same as the main checkout for that placement (`place`'s `Expected`), except that (i) is not listed, because its uncommitted file is only in the main checkout, and an uncommitted edit made in the linked worktree never shows. A planner probe on `main` (2026-11-22) built every placement in each kind, with and without `edit_uncommitted` applied in the linked worktree where the ticket file exists there, and confirmed these results.

Test `test_linked_worktree_placements` in `tests/test_ticket_placement_reads.py`: for each kind in (3, 4, 5) and each placement, build a fresh repository with `make_repo(self.tmp)` and `place(root, placement, 5)`, then `checkout(root, kind, 5)`, and compare `Repo.find(TASK-5)` and `Repo.tasks(context("tasks"), "all")` with the expected result the way `test_main_checkout_placements` does (or through `placement_mismatches` if `TASK-528` has landed by then; either is fine). Where `chitty/tasks/TASK-5--example.md` exists in the linked worktree, repeat with `edit_uncommitted(<checkout>, 5)` and the same expected result. Use `subTest(kind=..., placement=..., edit=...)`.

No property: fixed placements and kinds, each listed and tested; generated draws are `TASK-523`. No production code changes unless a test finds a bug.

## Acceptance Criteria

- [ ] `test_linked_worktree_placements` passes for kinds 3, 4 and 5 over every placement, with and without an uncommitted edit where the file exists in that worktree; changing (i)'s expected result in kind 4 to `uncommitted` makes it fail (shown once in a note)
- [ ] `make check` passes

## Notes

Split from `TASK-393` on 2026-11-21. Keep in planning until `TASK-393` lands; then compare with the landed builder, probe the expected results, cold-read and move to `todo`.

## History

- 2026-11-21T23:05:23Z lively-zinc-newt → planning
- 2026-11-21T23:06:00Z lively-zinc-newt: changed notes
- 2026-11-21T23:07:54Z lively-zinc-newt: changed description
- 2026-11-21T23:18:59Z lively-zinc-newt: changed dependencies
- 2026-11-22T00:19:30Z lively-zinc-newt: changed dependencies, description, acceptance criteria
- 2026-11-22T00:19:30Z lively-zinc-newt planning → cold-read
