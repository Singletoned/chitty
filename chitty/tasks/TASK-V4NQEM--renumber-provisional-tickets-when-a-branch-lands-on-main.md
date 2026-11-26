---
title: Renumber provisional tickets when a branch lands on `main`
status: cold-read
labels:
  - bug
created: 2026-11-26
provisional: true
---

## Description

### Why

Tickets added off `main` get provisional IDs (`Repo.new_id`), and only `chitty renumber` run on `main` gives them numbers. So a planner commits once more on `main` after every plan branch lands, and tickets a worker adds on a ticket branch keep provisional IDs after the runner lands it. Decided (the person, 2026-11-26): renumber provisional IDs automatically when a branch merges into `main`.

### Change

1. Renumbering is safe on any branch that contains `main`'s tip, because the fast-forward that follows refuses if `main` has moved. In `Repo._plan_provisional_renumbering` (`src/chitty/store.py`), raise `ProvisionalOffMain` only when the current branch is not `main` and `git.is_ancestor(self.root, <main branch>, "HEAD")` is false. Its message, and the bare-`renumber` message in `src/chitty/cli.py`, say to rebase onto `main` first.
2. In `_land_locked` (`src/chitty/run.py`), at both places that call `git.fast_forward(main_root, branch)`, renumber first, inside the same `locks.main_checkout_lock(main_root)` block: `Repo(worktree, main_repo.config).renumber_provisional()`, which commits on the ticket branch. Holding the lock means no other landing moves `main` in between. Put the two steps in one helper used by both places. Renumbering changes only ticket files, so the landing check does not rerun.

Plan and hotfix branches landed by hand get the same steps when TASK-340 adds `chitty land`; until then a planner runs `chitty renumber` after rebasing onto `main` and before fast-forwarding, with no commit on `main`.

### Out of scope

`chitty land` (TASK-340); renumbering shared IDs (TASK-660).

## Acceptance Criteria

- [ ] In `tests/test_landing.py` (`LandingTestCase`), the ticket branch also commits a provisional ticket (`provisional: true`, ID `TASK-ABCDEF`, written into its file directly) whose Description mentions its own ID; after `finish_ticket` and `land()`, `main` has that ticket as `TASK-2` with `moved_from: TASK-ABCDEF`, no file with the provisional ID, the mention rewritten, and a commit on the landed branch whose subject starts `chitty: renumber`. Fails without the change.
- [ ] In `tests/test_renumber_provisional.py`, bare `chitty renumber` on a branch that contains `main`'s tip renumbers its provisional tickets and commits on that branch, and on a branch that does not contain `main`'s tip it changes nothing and prints a message saying to rebase onto `main` first. Fails without the change. Regression tests: `tests/test_landing.py` and `tests/test_landing_retry.py` pass. `make check` passes.

## History

- 2026-11-26T17:46:59Z calm-ochre-quail → backlog
- 2026-11-26T17:48:35Z calm-ochre-quail: changed labels, description, acceptance criteria
- 2026-11-26T17:48:35Z calm-ochre-quail backlog → cold-read
