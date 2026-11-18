---
title: Keep `chitty fix` and pending landings to tickets read from this checkout
status: cold-read
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

- `fix` (which scans files with `scan`, not `Repo`) builds a map from path to `StoredTask` once from `Repo.tasks` over every context, and skips any ticket file whose ticket is read from another ref (`StoredTask.branch` is not `None`). When such a file was named explicitly, it prints `skipped <path>: read from <ref>` to stderr. So in a ticket worktree it also skips tickets read from `main`: intended. Lookup errors (duplicate IDs, diverged branches) propagate; never swallow them in the existing `except ChittyError: continue`. A diverged ticket therefore stops `fix`, `chitty run` and every command that reads all tickets: intended, loudly.
- Existing bug, fixed here: `fix` with an empty path list repairs every ticket (`check.py`, `wanted and ...`), and `_commit` passes an empty list when the only change path was deleted (`_delete_done` in delete mode). An explicitly empty list now repairs nothing; only `chitty fix` with no arguments scans everything. `chitty check` keeps checking every file in this checkout, as a file-format check.
- `_land_pending` lands a branch only when `find` read the ticket from that local branch (`stored.branch == <local branch name>`); otherwise it skips the branch silently, so a later run lands it after the local branch catches up. Equal local and remote tips read from the local branch (`TASK-377` prefers it), so a pushed `done` ticket still lands.

Tests: real-Git tests in a new `tests/test_fix_and_landing_sources.py`, inheriting `CliTestCase` from `tests/test_cli.py`. No property: two fixed caller rules over the cases in the criteria.

## Acceptance Criteria

- [ ] In the main checkout, with `TASK-5` in flight on `task-5` and `main`'s copy of its file holding `depends_on: [task-3]` in lower case (committed directly with Git), `chitty fix` leaves that file byte-identical and makes no commit, while it rewrites the same defect to `TASK-3` in a ticket with no branch; the first part fails before the change
- [ ] `_land_pending` with local `task-5` saying `doing` and `origin/task-5` ahead saying `done` lands nothing and leaves `main` unchanged; with `origin/task-5` at the same commit as a local `task-5` saying `done`, it lands; `make check` passes
- [ ] Archiving a `done` ticket in delete mode that no other ticket references leaves every other ticket file byte-identical, even one with a fixable defect; this fails before the change

## History

- 2026-11-18T16:38:05Z lively-quartz-crane → backlog
- 2026-11-18T16:39:35Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:39:35Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:44Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:51:22Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:51:22Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:51:24Z lively-quartz-crane planning → cold-read
