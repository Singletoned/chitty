---
title: Count other branches' tickets when allocating an ID
status: backlog
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

Parallel ticket branches hand out the same IDs, and the clash only shows up when they merge. `Repo.next_number` in `src/chitty/store.py` returns the highest number among task files in the current checkout plus one, so it never sees tickets committed on other branches. In `echonomicon` on 2026-11-04, review follow-ups filed from separate worktrees collided: `TASK-24` was created on three branches within six minutes, and `TASK-25` to `TASK-27` the same way. After merging, `chitty check` fails, `Task: <ID>` trailers and notes become ambiguous, `chitty show` can display the wrong ticket, and `chitty next` can name an ambiguous ID.

Have `next_number` also count every ticket file in this context, active and archived, from `self._history()`, which already reads the newest committed files from all local and remote-tracking branches. `move` uses the same function, so it gains this too.

This does not cover uncommitted tickets in another worktree, which is what `autocommit = false` leaves, or unpushed work on another machine. Both are accepted: say so in `PLAN.md`, where it describes creating tickets.

Split on 2026-11-05: repairing a collision that has already happened, and giving tickets raised on branches their own IDs, are separate tickets.

## Acceptance Criteria

- [ ] A test with a ticket committed only on another branch, with no worktree, shows `chitty add` on `main` taking the number above it, in both active and archived locations, and fails without the change
- [ ] `PLAN.md` says what allocation sees and what it cannot

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-05T09:16:09Z upbeat-quail → backlog
- 2026-11-05T09:16:10Z upbeat-quail: changed notes
- 2026-11-05T14:43:39Z mellow-newt: changed title, priority, parent, description, acceptance criteria
