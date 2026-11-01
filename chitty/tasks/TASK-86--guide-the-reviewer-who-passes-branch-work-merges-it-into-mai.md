---
title: "Guide: the reviewer who passes branch work merges it into `main`"
status: review
priority: high
created: 2026-11-01
---

## Description

Decided with the human (2026-11-01): for now, the reviewer who passes a ticket merges its branch back into `main` and removes the branch and worktree, to see how that goes. The managed guide should say so. The broader worktree guidance stays in TASK-85.

## Acceptance Criteria

- [x] The managed guide says the reviewer who passes branch work merges it into `main` and removes the branch and its worktree
- [x] `PLAN.md`'s copy of the guide matches; `version` is bumped and `chitty init` refreshed here

## Plan

Add one sentence to the review bullet in `src/chitty/guide.md` and `PLAN.md`'s guide copy, bump the patch version (current per-change rule until TASK-80 lands), run `chitty init`, `make check`.

## History

- 2026-11-01 → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
