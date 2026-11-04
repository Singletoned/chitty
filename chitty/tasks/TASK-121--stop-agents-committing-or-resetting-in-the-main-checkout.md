---
title: Stop agents committing or resetting in the main checkout
status: backlog
priority: medium
depends_on:
  - TASK-126
  - TASK-129
created: 2026-11-03
---

## Description

The global `chitty` runs whatever the main checkout contains. On 2026-11-03 the TASK-107 worker committed its `doing` claim on `main` by mistake, then ran `git reset --hard` in the main checkout to undo it (Pi session `2026-11-03T10-42-23`). A branch switch in main would also change `chitty` for every repository. Find a guard that makes this fail loudly, for example a hook or a clearer claim flow. See `TASK-118`.

## Acceptance Criteria

- [ ] A worker that tries to implement or switch branches in the main checkout is stopped or warned loudly

## Notes

`TASK-126` covers Pi: `chitty run` makes the claim, and the extension refuses to start outside a linked worktree. What remains is other agents and manual sessions. Re-scope once that lands.

Cold-read this after `TASK-126` lands and it has been re-scoped, because its text will change.

Depends on `TASK-129` so that lands first after `TASK-126`.

Moved back to `backlog` on 2026-11-04, under the new rule that a ticket stays there until its cold read has outcomes. A cold read is running.

Cold read by a fresh Sonnet subagent, 2026-11-04. Mostly obsolete, so left in `backlog`. `TASK-126` makes the claim in the worktree, refuses to run off `main`, and the Pi extension refuses to start outside a linked worktree, so claiming on `main` is closed for `chitty run`. It has not been re-scoped, as its note asked, and it names no mechanism. What remains is agents and people started by hand or on other harnesses, which belongs with `TASK-89` and `TASK-90` if it proves to happen. Left for the human to close or keep.

Closed unbuilt by the human on 2026-11-04. Not needed: `TASK-126` closed the problem for `chitty run`. Raise it again with `TASK-89` and `TASK-90` if agents started by hand cause it.

## History

- 2026-11-03T11:39:03Z eager-raven → todo
- 2026-11-03T16:30:16Z lively-panda: changed notes
- 2026-11-03T16:31:24Z lively-panda: changed dependencies
- 2026-11-03T18:18:20Z lively-panda: changed notes
- 2026-11-03T20:44:57Z lively-panda: changed dependencies, notes
- 2026-11-04T09:45:41Z lively-panda: changed priority
- 2026-11-04T15:30:42Z mellow-newt: changed notes
- 2026-11-04T15:30:42Z mellow-newt todo → backlog
- 2026-11-04T15:31:50Z mellow-newt: changed notes
- 2026-11-04T15:33:52Z mellow-newt: changed notes
