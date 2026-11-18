---
title: Keep `chitty fix` and pending landings to tickets read from this checkout
status: planning
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-18
---

## Description

After `TASK-378`, a ticket in flight is read from its branch, but two callers still act on this checkout's copy of it:

- `chitty fix` (`fix` in `src/chitty/check.py`) scans and rewrites this checkout's ticket files, so in the main checkout it can reformat or rename `main`'s stale copy of a ticket that is in flight, a write on `main` for a ticket with a branch, which the new model forbids (`docs/plan/ticket-state.md`, on branch `plan/ticket-state` until it lands on `main`).
- `_land_pending` in `src/chitty/run.py` lands each local ticket branch whose ticket says `done`, using `main_repo.find`. If `origin/task-<n>` is ahead of the local branch, `find` reads the remote copy, so a `done` there would land the local branch, which may not have it.

Starts after `TASK-378` lands.

Decisions:

- `fix` skips any ticket file whose ticket `Repo` reads from another ref (`StoredTask.branch` is not `None`), and reports nothing for it. `chitty check` keeps checking every file in this checkout, as a file-format check.
- `_land_pending` lands a branch only when `find` read the ticket from that local branch (`stored.branch == <local branch name>`); otherwise it skips the branch silently, so a later run lands it after the local branch catches up.

Tests: real-Git tests in a new `tests/test_fix_and_landing_sources.py`, inheriting `CliTestCase` from `tests/test_cli.py`. No property: two fixed caller rules over the cases in the criteria.

## Acceptance Criteria

- [ ] In the main checkout, with `TASK-5` in flight on `task-5` and `main`'s copy of its file badly formatted (committed directly with Git), `chitty fix` leaves that file byte-identical and makes no commit, while it still fixes a badly formatted ticket with no branch; the first part fails before the change
- [ ] `_land_pending` with local `task-5` saying `doing` and `origin/task-5` ahead saying `done` lands nothing and leaves `main` unchanged; with the local branch saying `done` it lands as before; `make check` passes

## History

- 2026-11-18T16:38:05Z lively-quartz-crane → backlog
- 2026-11-18T16:39:35Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:39:35Z lively-quartz-crane backlog → planning
