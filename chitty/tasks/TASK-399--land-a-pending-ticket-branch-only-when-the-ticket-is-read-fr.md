---
title: Land a pending ticket branch only when the ticket is read from it
status: cold-read
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-18
---

## Description

`_land_pending` in `src/chitty/run.py` lands each local ticket branch whose ticket says `done`, using `main_repo.find`. After `TASK-378`, `find` reads the ticket from the authoritative ref, which may be `origin/task-<n>` when that is ahead of the local branch; a `done` there would land the local branch, which may not have it. Context: `docs/plan/ticket-state.md`, "Planning decisions" (on branch `plan/ticket-state` until it lands on `main`).

Starts after `TASK-378` lands.

Decisions:

- `_land_pending` lands a branch only when `find` read the ticket from that local branch (`stored.branch == <local branch name>`). Otherwise it prints `not landing <branch>: <ID> is read from <ref>` to stderr and moves on, so a later run lands it once the local branch catches up. Equal local and remote tips read from the local branch (`TASK-377` prefers it), so a pushed `done` ticket still lands. The main checkout is on `main` when landing (`_land_locked` requires it), so a `None` source never arises here.
- A `ticket_source` error for one ticket (diverged branches, changed on both sides) propagates and stops the run, loudly, as decided.

Tests: real-Git runner tests in a new `tests/test_land_pending_source.py`, in the style of `tests/test_landing.py` (configured `setup` and `check`), with `origin/task-5` made by `git update-ref`. No property: three fixed tip relations, each in the criteria.

## Acceptance Criteria

- [ ] With local `task-5` saying `doing` and `origin/task-5` ahead saying `done`, `_land_pending` returns no result, prints `not landing task-5:` to stderr, and leaves `git rev-parse main` unchanged; this fails before the change
- [ ] With `origin/task-5` at the same commit as a local `task-5` saying `done`, `_land_pending` lands it: `main`'s tip equals the branch tip afterwards; with no remote, it lands as before; `make check` passes

## History

- 2026-11-18T17:54:14Z lively-quartz-crane → backlog
- 2026-11-18T17:55:05Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T17:55:05Z lively-quartz-crane backlog → planning
- 2026-11-18T17:56:22Z lively-quartz-crane planning → cold-read
