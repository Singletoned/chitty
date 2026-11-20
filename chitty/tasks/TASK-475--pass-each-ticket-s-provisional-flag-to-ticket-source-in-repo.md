---
title: Pass each ticket's `provisional` flag to `ticket_source` in `Repo.source_copy`
status: doing
depends_on:
  - TASK-476
parent: TASK-376
created: 2026-11-20
---

## Description

`TASK-476` adds `Repo.source_copy(task_id)` in `src/chitty/store.py`, which calls `ticket_source` (`src/chitty/ticket_source.py`) from `Repo._choose_source` with `False` as its second (`provisional`) argument for every ID. A provisional ticket (`provisional: true` in its frontmatter, `Frontmatter.provisional` in `src/chitty/model.py`, given a provisional ID by `Repo.new_id`) is created on the branch where it is written and is read from that checkout's working tree (`docs/plan/ticket-state.md`, "Planning decisions": "or when X is provisional (created on this branch)"; on branch `plan/ticket-state` until it lands). This ticket passes the real flag. Split out of `TASK-474` and `TASK-476`; `TASK-378` wires `source_copy` into reads after both land.

Decisions:

- `provisional` is true when the first copy found, in this order: this checkout's working tree, then `main`'s tip (from `Repo._ticket_ref_files`, no extra Git call), has `provisional: true`. Active and archive copies both count, as `source_copy` finds them. Ticket branches are not consulted: a ticket branch is named after a numbered ID, and a provisional ID is random. Only that one copy is parsed to decide it; its parse error propagates as `TASK-476` formats parse errors.
- `ticket_source` then returns `WORKING_TREE`, so `source_copy` reads this checkout's file, or gives `None` when this checkout has none. A provisional ticket found only at `main`'s tip therefore gives `None` in a checkout without the file: intended, because a provisional ticket belongs to the checkout that made it.
- A provisional ticket on another branch is not in `ticket_ids` from this checkout unless the branch is named after its ID (`TASK-474`'s rule), so no other case arises.

Tests: add to `tests/test_source_copy.py` (from `TASK-476`), with real Git as that file does; make a provisional ticket with `chitty add` in a checkout that is not on `main` (`Repo.new_id` then gives a provisional ID and sets `provisional: true`), or by committing a file with `provisional: true` added to its frontmatter (the `file()` helper in `tests/test_source_copy.py` writes none). A provisional ID is random, so it never matches the branch name. For the worktree case, open `Repo.open(<worktree>)` and run `chitty add` with the worktree as the current directory. No property: three fixed cases, each in the criteria.

## Acceptance Criteria

- [ ] In a test repository, in a linked worktree the test makes on a new branch `task-5` (`git worktree add`, so not on `main`), a ticket created there with `chitty add` gets a provisional ID and `provisional: true`; it gives `ref` `None` and its working-tree content, both before and after it is committed on `task-5` (fails before the change: with `provisional=False` it gives `None`, as `main` has no file for it)
- [ ] In a checkout on branch `feature`, made from `main` after committing the fixture there: a ticket whose `main` copy has `provisional: true`, with the file deleted in the working tree, gives `None`, and the same ticket without `provisional` gives `ref` `main`; a ticket whose working-tree copy has no `provisional` while its `main` copy has `provisional: true` gives `ref` `main` (only the first copy found decides)
- [ ] In a checkout on branch `feature`, with the working-tree copy of a ticket broken by removing its closing `---` while `main`'s copy is well formed, `source_copy` raises `ChittyError` whose message starts with the absolute working-tree path and contains `frontmatter is not closed` (fails before the change, which reads `main`'s copy). `make check` passes

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
- 2026-11-20T20:05:30Z jolly-dusky-badger: changed description
- 2026-11-20T20:05:30Z jolly-dusky-badger planning → cold-read
- 2026-11-20T20:06:35Z jolly-dusky-badger: changed description, acceptance criteria
- 2026-11-20T20:06:35Z jolly-dusky-badger cold-read → todo
- 2026-11-20T20:07:02Z golden-umber-toad todo → doing
