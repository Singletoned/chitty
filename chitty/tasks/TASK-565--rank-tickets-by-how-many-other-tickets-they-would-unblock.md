---
title: Rank tickets by how many other tickets they would unblock
status: backlog
created: 2026-11-22
---

## Description

Requested by the owner on 2026-11-21: "Chitty should have a way of telling you which tickets would unblock the most other tickets."

Today `chitty list` marks `🚧` on active chain endpoints that have waiting dependents (`docs/plan/next-action-and-runner.md`), but gives no count. Neither `list` nor `next` says which ticket would release the most waiting work, so a human or planner deciding what to refine or work next cannot tell. Most stuck work is in `planning`: on 2026-11-21 there were 18 `planning` tickets and several `todo` tickets marked `🔗` (waiting on a dependency).

Working this out by hand is slow. A script running `chitty show` for each active ticket to read its authoritative `depends_on` took over two minutes. Reading `chitty/*/*.md` in the main checkout is quick but wrong, because tickets in flight have newer copies on their branches (for example, TASK-378 is `blocked` in the main checkout but `todo` on its branch, with more dependencies).

Possible shape, to be decided in planning: for each active ticket, the number of active tickets that depend on it directly or transitively, shown in `chitty list`, perhaps as a sort order or a count next to `🚧`. `chitty next` (and so `chitty run`) could also use the count to break ties within a priority. Keep the surface small: prefer extending `list` or `next` over a new command.

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:35Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:36Z friendly-jade-stoat: changed notes
