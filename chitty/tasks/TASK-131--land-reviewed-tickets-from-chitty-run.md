---
title: Land reviewed tickets from `chitty run`
status: todo
priority: medium
depends_on:
  - TASK-120
  - TASK-150
parent: TASK-106
created: 2026-11-03
---

## Description

This follows `TASK-120` and `TASK-150`, which rebase and check before a review. After a pass, have `chitty run` land the work, so reviewers no longer merge in the main checkout, where a conflict breaks `chitty` for every repository (`TASK-118`). Logic goes in `src/chitty/run.py`, with Git helpers in `src/chitty/git.py`.

### Landing a `done` ticket

After a session that moves its ticket to `done`. `TASK-151` adds the refusals for checkouts that are not clean, and `TASK-152` adds landing at the start of a run:

1. If `main` is not an ancestor of the branch, rebase the branch onto `main` in its worktree, then run `setup` and `check`. Ticket commits land on `main` often, so this will be common. A clean rebase with a passing `check` lands without another review. On a conflict or failed check, abort any rebase, leave everything in place, and exit non-zero naming the problem, for the human to resolve in the worktree.
2. Run `git merge --ff-only <branch>` in the main checkout. Never resolve anything there. `TASK-134` then refreshes setup at the start of the next run.
3. Remove the worktree with `git worktree remove` and the branch with `git branch -d`, never forced. A failure exits non-zero.

### Prompts and docs

The Pi review prompt stops telling the reviewer to merge or remove anything. `src/chitty/guide.md` tells agents without `chitty run` to rebase the branch onto `main` in the worktree first, then only fast-forward `main`.

Out of scope: pushing, repositories whose main branch is not `main`, the spec-test gates for the pilot's tests stage, and non-Pi harnesses.

## Acceptance Criteria

- [ ] Tests cover landing when `main` has moved: a clean rebase with a passing `check` lands, while a conflict or failing `check` leaves everything in place and exits non-zero, and a later run lands it once resolved
- [ ] A Node test shows the review prompt no longer mentions merging or removing
- [ ] `PLAN.md`, `README.md` and `src/chitty/guide.md` describe landing; `__version__` is bumped above `main`'s
- [ ] Tests show a passed review fast-forwarding `main` with a linear history, the ticket `done` there, and the worktree and branch removed

## Notes

The `chitty init` step and its criterion moved to `TASK-134`, at the start of every run, as suggested by the human.

From the `TASK-134` cold read: carrying on to selection after landing would have started the next agent on old code, so a landing now ends the run.

Split on 2026-11-04 at the human's direction, from eight criteria: refusals are now `TASK-151` and landing at the start of a run is `TASK-152`.

## History

- 2026-11-03T20:46:17Z lively-panda → todo
- 2026-11-03T21:21:53Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T21:24:18Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T09:45:41Z lively-panda: changed priority
- 2026-11-04T15:11:37Z mellow-newt: changed dependencies, description, acceptance criteria, notes
