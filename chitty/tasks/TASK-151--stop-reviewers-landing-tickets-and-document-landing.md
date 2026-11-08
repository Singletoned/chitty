---
title: Stop reviewers landing tickets, and document landing
status: todo
priority: high
depends_on:
  - TASK-131
parent: TASK-106
created: 2026-11-04
---

## Description

`TASK-131` has `chitty run` land a ticket after a pass, so reviewers should stop doing it. The Pi review prompt in `src/chitty/integrations/pi/chitty.ts` stops telling the reviewer to merge or remove anything. `src/chitty/guide.md` tells agents without `chitty run` to rebase the branch onto `main` in the worktree first, then only fast-forward `main`. If `TASK-141` has landed, make the same change in `src/chitty/roles/review.md`, and to whatever now produces the prompt.

`PLAN.md` and `README.md` describe landing.

Out of scope: changing landing itself.

## Acceptance Criteria

- [ ] A test shows the review instructions no longer mentioning merging or removing
- [ ] `PLAN.md`, `README.md`, and `src/chitty/guide.md` describe landing; the ticket branch does not bump `__version__`.

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Repurposed: its refusals moved back into `TASK-131`, because landing without them was unsafe, and this now holds the prompt and documentation part.

TASK-224 supersedes the branch-version-bump requirement; version selection happens at release.

## History

- 2026-11-04T15:11:35Z mellow-newt → todo
- 2026-11-04T15:17:39Z mellow-newt: changed title, description, acceptance criteria, notes
- 2026-11-06T16:24:15Z youthful-toad: changed priority
- 2026-11-08T13:05:15Z eager-puffin: changed acceptance criteria, notes
