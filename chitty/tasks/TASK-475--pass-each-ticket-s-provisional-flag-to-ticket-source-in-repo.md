---
title: Pass each ticket's `provisional` flag to `ticket_source` in `Repo.source_copy`
status: planning
depends_on:
  - TASK-476
parent: TASK-376
created: 2026-11-20
---

## Description

`TASK-476` adds `Repo.source_copy(task_id)` in `src/chitty/store.py`, which calls `ticket_source` (`src/chitty/ticket_source.py`) with `provisional=False` for every ID. A provisional ticket (`provisional: true` in its frontmatter, `Frontmatter.provisional` in `src/chitty/model.py`, given a provisional ID by `Repo.new_id`) is created on the branch where it is written and is read from that checkout's working tree (`docs/plan/ticket-state.md`, "Planning decisions": "or when X is provisional (created on this branch)"; on branch `plan/ticket-state` until it lands). This ticket passes the real flag. Split out of `TASK-474` and `TASK-476`; `TASK-378` wires `source_copy` into reads after both land.

Decisions:

- `provisional` is true when the first copy found, in this order: this checkout's working tree, `main`'s tip, the ticket branch's tip (the same copies `TASK-474` reads, no extra Git call), has `provisional: true`. Only that copy is parsed to decide it; its parse error propagates as `TASK-476` formats parse errors.
- `ticket_source` then returns `WORKING_TREE`, so `source_copy` reads this checkout's file, or gives `None` when this checkout has none. A provisional ticket found only at `main`'s tip therefore gives `None` in a checkout without the file: intended, because a provisional ticket belongs to the checkout that made it.
- A provisional ticket on another branch is not in `ticket_ids` from this checkout unless the branch is named after its ID (`TASK-474`'s rule), so no other case arises.

Tests: add to `tests/test_source_copy.py` (from `TASK-476`), with real Git as that file does; make a provisional ticket with `chitty add` in a checkout that is not on `main` (`Repo.new_id` then gives a provisional ID and sets `provisional: true`), or by committing a file with `provisional: true`. No property: three fixed cases, each in the criteria.

## Acceptance Criteria

- [ ] In a test repository, in a linked worktree the test makes on a new branch `task-5` (`git worktree add`, so not on `main`), a ticket created there with `chitty add` gets a provisional ID and `provisional: true`; it gives `ref` `None` and its working-tree content, both before and after it is committed on `task-5` (fails before the change: with `provisional=False` it gives `None`, as `main` has no file for it)
- [ ] A ticket whose `main` tip copy has `provisional: true`, read from a checkout on branch `feature` whose working tree has deleted the file, gives `None`; the same ticket without `provisional` gives `ref` `main`
- [ ] In a checkout on branch `feature`, with a malformed working-tree copy of a ticket that also exists, well formed, at `main`'s tip, `source_copy` raises the working-tree parse error (`<absolute path>: <error>`), because that copy is parsed first (fails before the change, which reads `main`'s copy); `make check` passes

## Notes

Planner, 2026-11-20: cold-read once; stays in `planning` because it builds on `Repo.source_copy` from `TASK-476`, not yet landed. When `TASK-476` is done, compare this text with what landed, cold-read again, then move to `todo`.

## History

- 2026-11-20T12:41:32Z jolly-dusky-badger → planning
- 2026-11-20T12:41:44Z jolly-dusky-badger: changed acceptance criteria
- 2026-11-20T12:41:59Z jolly-dusky-badger: changed description
- 2026-11-20T12:43:53Z jolly-dusky-badger planning → cold-read
- 2026-11-20T12:44:31Z jolly-dusky-badger: changed acceptance criteria, notes
- 2026-11-20T12:44:31Z jolly-dusky-badger cold-read → planning
- 2026-11-20T17:44:33Z jolly-dusky-badger: replaced notes; changed dependencies, description, acceptance criteria
