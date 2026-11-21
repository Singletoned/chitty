---
title: Land a pending ticket branch only when the ticket is read from it
status: doing
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-18
---

## Description

`_land_pending` in `src/chitty/run.py` lands each local ticket branch whose ticket says `done`, using `main_repo.find`. After `TASK-378`, `find` reads the ticket from the authoritative ref, which may be `origin/task-<n>` when that is ahead of the local branch; a `done` there would land the local branch, which may not have it. Context: `docs/plan/ticket-state.md`, "Planning decisions" (on branch `plan/ticket-state` until it lands on `main`).

Starts after `TASK-378` lands.

Decisions:

- `_land_pending` lands a branch only when `find` read the ticket from that local branch (`stored.branch == <local branch name>`; `TASK-378` makes `branch` the short name). The check sits before the landing in its loop, so a skipped branch does not stop the next one from landing. Otherwise it prints `not landing <branch>: <ID> is read from <ref>` to stderr and moves on, so a later run lands it once a person fast-forwards the local branch (`git merge --ff-only origin/task-5` in its worktree); the line repeats on every run until then, including each `--loop` cycle: accepted, as a visible reminder. Equal local and remote tips read from the local branch (`TASK-377` prefers it), so a pushed `done` ticket still lands. The main checkout is on `main` when landing (`_land_locked` requires it), so a `None` source never arises here.
- A `ticket_source` error for one ticket (diverged branches, changed on both sides) propagates and stops the run, loudly, as decided.

Tests: real-Git runner tests in a new `tests/test_land_pending_source.py`, in the style of `tests/test_landing.py` (configured `setup` and `check`), with a ticket numbered 5 (the `setUp` makes `TASK-1`), `origin/task-5` made by `git commit-tree` on the branch tip and `git update-ref`, and stderr captured. No property: a fixed set of tip relations (remote ahead, equal, local ahead, no remote), each in the criteria.

## Acceptance Criteria

- [ ] With local `task-5` saying `doing` and `origin/task-5` ahead saying `done`, `_land_pending` returns no result, prints `not landing task-5:` to stderr, and leaves `git rev-parse main` unchanged; this fails before the change
- [ ] With local `task-5` saying `done` ahead of `origin/task-5`, `_land_pending` lands it: `main`'s tip equals the branch tip afterwards
- [ ] Regression guards: equal local and remote tips, and no remote at all, still land; with two pending branches where the first is skipped, the second lands; `make check` passes

## Plan

Add real-Git pending-landing source tests for remote-ahead, local-ahead, equal, absent remote, and skip-then-land cases; confirm the remote-ahead regression fails first. Filter completed candidates by their source branch, reporting mismatches, then run formatting and checks.

## History

- 2026-11-18T17:54:14Z lively-quartz-crane → backlog
- 2026-11-18T17:55:05Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T17:55:05Z lively-quartz-crane backlog → planning
- 2026-11-18T17:56:22Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:58:24Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:58:24Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:58:26Z lively-quartz-crane planning → todo
- 2026-11-21T13:08:36Z nimble-ebony-marten todo → doing
- 2026-11-21T13:10:31Z nimble-ebony-marten: wrote the plan
