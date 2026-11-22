---
title: Check ticket reads from the ticket's own worktree against every placement
status: doing
labels:
  - question
depends_on:
  - TASK-522
parent: TASK-393
created: 2026-11-22
---

## Description

Split from `TASK-522` on 2026-11-22. `TASK-522` reads every placement from linked worktrees that are not the ticket's own. This ticket reads from the ticket's own worktree (kind 2), where `current_branch` matters in `Repo._choose_source` (`src/chitty/store.py`), and adds a mutant test for it. `TASK-522` landed `checkout(root, kind, number)` in `tests/ticket_placements.py` for kinds 3 to 5 (raising `ValueError` otherwise) and `test_linked_worktree_placements` in `tests/test_ticket_placement_reads.py` (rechecked on `main` 2026-11-22). Add a `kind == 2` branch to `checkout`, and a `test_own_worktree_placements` that follows `test_linked_worktree_placements`'s pattern, with the kind-2 expectations below written in the test rather than taken from `place`.

Kind 2: `git worktree add <root>/.worktrees/task-<n> task-<n>`, returning that path, only for placements with a local branch: (b), (d), (e), (g), (h), (j), (k), (l).

Expected results, read with `Repo.open(<worktree>)` (`find(TASK-5)` and `tasks(context("tasks"), "all")`), confirmed by a planner probe and a cold reader's probe on `main` 2026-11-22. Write this table in the test; loop over exactly these placements and variants:

| placement | no edit | with `edit_uncommitted(<worktree>, 5)` |
| --- | --- | --- |
| b | `branch` | `uncommitted` |
| d | `remote` | not run (open question below) |
| e | error containing `` `origin/task-5` `` and `` `task-5` `` | same error |
| g | `branch`, archived | not run (the active file is gone there) |
| h | not listed (`find` raises containing `no task`; `tasks` gives `[]`) | same |
| j | `main-2` | `main-2` |
| k | error containing `` `task-5` `` and `` `main` `` (`changed on both`) | same error |
| l | `remote` | `remote` |

Open question (recorded for the owner): in (d) with an uncommitted edit in the worktree the read gives `uncommitted`, although `ticket_source` returns `origin/task-<n>` for that state and (l) hides the edit. Leave that variant out until the owner decides whether it is a bug.

Test mechanism: add a module-level function `own_worktree_mismatches(parent: Path) -> list[str]` in `tests/test_ticket_placement_reads.py` that builds a fresh repository for each row and variant (`make_repo(parent)`, `place(root, placement, 5)`, `checkout(root, 2, 5)`, then `edit_uncommitted` on the worktree for the edit variant), compares the reads with the table, and appends one string `"<placement> edit=<edit>: <what differed>"` per difference; it catches only `ChittyError`. `test_own_worktree_placements` asserts it returns `[]`. `test_own_worktree_mutant_main_branch` patches `chitty.store.ticket_source` with a wrapper that replaces the 3rd positional argument `current_branch` with the literal `"main"` and asserts the list is non-empty (the probe shows (b) with an edit then reads `branch`).

## Acceptance Criteria

- [ ] `test_own_worktree_placements` passes (the collector returns `[]` for every row and variant in the table) and `test_own_worktree_mutant_main_branch` passes (non-empty list under the mutant); `make check` passes

## History

- 2026-11-22T00:19:27Z lively-zinc-newt → planning
- 2026-11-22T00:40:44Z lively-zinc-newt: changed description
- 2026-11-22T00:40:44Z lively-zinc-newt planning → cold-read
- 2026-11-22T00:42:23Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T00:42:23Z lively-zinc-newt cold-read → todo
- 2026-11-22T01:31:44Z tidy-lilac-crane todo → doing
