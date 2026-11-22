---
title: Check ticket reads from the ticket's own worktree against every placement
status: planning
labels:
  - question
depends_on:
  - TASK-522
parent: TASK-393
created: 2026-11-22
---

## Description

Split from `TASK-522` on 2026-11-22. `TASK-522` reads every placement from linked worktrees that are not the ticket's own. This ticket reads from the ticket's own worktree (kind 2), where `current_branch` matters in `Repo._choose_source` (`src/chitty/store.py`), and adds a mutant test for it. Draft: keep in planning until `TASK-522` lands (it adds `checkout`), then add kind 2 to it, check, cold-read.

Kind 2: `git worktree add .worktrees/task-<n> task-<n>`, only for placements with a local branch: (b), (d), (e), (g), (h), (j), (k), (l).

Expected, confirmed by a planner probe on `main` 2026-11-22: (b) `branch`, or `uncommitted` with an uncommitted edit in that worktree; (g) `branch`, archived (the active file is gone there, so no edit variant); (h) not listed; (d) `remote`; (e) `diverged refs`; (k) `changed on both` `task-<n>` and `main`; (j) `main-2`, and an edit does not show; (l) `remote`, and an edit does not show.

Open question (recorded for the owner): in (d) with an uncommitted edit in the worktree the probe reads `uncommitted`, although `ticket_source` returns `origin/task-<n>` for that state and (l) hides the edit. Leave the (d) edit variant out of the test until the owner decides whether it is a bug.

Mutant test: patch `chitty.store.ticket_source` with a wrapper that passes `Repo._main_branch()` as `current_branch` (3rd positional argument), as `test_mutant_ignores_current_branch` in `tests/test_source_copy_checkouts.py` does, and assert at least one kind-2 check differs (the (b) edit variant should read `branch`).

## Acceptance Criteria

- [ ] Every kind-2 placement and edit variant listed in the Description gives its expected result; the `current_branch` mutant test passes; `make check` passes

## History

- 2026-11-22T00:19:27Z lively-zinc-newt → planning
