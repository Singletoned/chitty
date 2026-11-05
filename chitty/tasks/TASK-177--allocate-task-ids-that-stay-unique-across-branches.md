---
title: Allocate task IDs that stay unique across branches
status: backlog
created: 2026-11-05
---

## Description

Parallel ticket branches hand out the same IDs, and the clash only shows up when they merge. `Store.next_number` in `src/chitty/store.py` returns the highest number among task files in the current checkout plus one (`ids.next_number`), so it never sees tickets committed on other branches. In `echonomicon` on 2026-11-04, review follow-ups filed from separate worktrees (`autocommit = false`, `archive = "move"`) collided: `TASK-24` was created at 21:13:06Z on `task-4-diagnostics-duplicates`, 21:17:04Z on `task-10-error-handling` and 21:18:32Z on `task-6-repeat-report`, each after the earlier one was committed or about to be, on a branch that could not see it. `TASK-25`, `TASK-26` and `TASK-27` collided the same way, giving four tickets for `TASK-24` to `TASK-27` in places. Consequences: `chitty check` fails after merging, `Task: <ID>` trailers and notes become ambiguous, `chitty show` from a worktree can display the other ticket of that number, and `chitty next` can name an ambiguous ID. The workflow makes this likely because every ticket gets its own branch and reviewers are told to file out-of-scope findings as new tickets there. Options: have allocation consider task files on all local branches (`chitty` already reads other branches to route writes), which covers local parallel work but not unpushed work elsewhere; or use IDs that cannot collide. Also needed: a `chitty renumber` command, since repairing a collision today means hand-editing task files and every reference, and `chitty fix` cannot do it. Note `TASK-84` records ID allocation as out of scope, so this may need its own ticket.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-05T09:16:09Z upbeat-quail → backlog
- 2026-11-05T09:16:10Z upbeat-quail: changed notes
