---
title: Runner misreads a worktree with uncommitted partial work as an empty branch
status: backlog
created: 2026-11-24
---

## Description

In echonomicon on 2026-11-23, TASK-195 went `doing` -> `planning` with a worker note saying implementation was incomplete, leaving `src/echonomicon/subscriptions.py` and `src/echonomicon/title_keys.py` modified but uncommitted in `.worktrees/task-195`. After the planner returned it to `todo`, the runner's pre-check ran `make lint test` in that worktree, failed (17 failures, 10 errors from the half-done change), and set `error` with "the branch has no work yet, so `main` fails this check". That message is wrong: `main` passes; the failures come from the uncommitted changes.

Suggestions: (1) when a worker session ends, the runner should commit or explicitly report uncommitted changes in the ticket worktree instead of leaving them; (2) the pre-check should notice a dirty worktree and say so, rather than blaming `main`; (3) a worker should never move a ticket to `planning` while saying in its own note that no planning is needed.

## Notes

Suggestion origin: echonomicon

Triage 2026-11-24: merged the leftover-edits parts of TASK-670 and TASK-687, which report the same TASK-195 and TASK-197 cases: (1) commit leftover changes as a WIP commit on the ticket branch, or report them loudly, before changing status; (2) the pre-check should tell failures caused by uncommitted worktree changes from failures on `main`. Related: TASK-491 (refuse moving a ticket out of `doing` while its worktree is dirty) and TASK-496 (tell environment failures from ticket failures).

## History

- 2026-11-24T22:21:39Z zesty-coral-newt → backlog
- 2026-11-24T22:21:39Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:33Z zesty-coral-newt: changed notes
