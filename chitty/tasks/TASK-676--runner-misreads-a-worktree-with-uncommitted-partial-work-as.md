---
title: Runner misreads a worktree with uncommitted partial work as an empty branch
status: backlog
priority: high
created: 2026-11-24
---

## Description

In echonomicon on 2026-11-23, TASK-195 went `doing` -> `planning` with a worker note saying implementation was incomplete, leaving `src/echonomicon/subscriptions.py` and `src/echonomicon/title_keys.py` modified but uncommitted in `.worktrees/task-195`. After the planner returned it to `todo`, the runner's pre-check ran `make lint test` in that worktree, failed (17 failures, 10 errors from the half-done change), and set `error` with "the branch has no work yet, so `main` fails this check". That message is wrong: `main` passes; the failures come from the uncommitted changes.

Suggestions: (1) when a worker session ends, the runner should commit or explicitly report uncommitted changes in the ticket worktree instead of leaving them; (2) the pre-check should notice a dirty worktree and say so, rather than blaming `main`; (3) a worker should never move a ticket to `planning` while saying in its own note that no planning is needed.

## Notes

Suggestion origin: echonomicon

Triage 2026-11-24: merged the leftover-edits parts of TASK-670 and TASK-687, which report the same TASK-195 and TASK-197 cases: (1) commit leftover changes as a WIP commit on the ticket branch, or report them loudly, before changing status; (2) the pre-check should tell failures caused by uncommitted worktree changes from failures on `main`. Related: TASK-491 (refuse moving a ticket out of `doing` while its worktree is dirty) and TASK-496 (tell environment failures from ticket failures).

Triage 2026-11-25: merged TASK-10018 (chitty `TASK-651`: a previous worker's uncommitted edits to `src/chitty/store.py` and three test files in `.worktrees/task-651` failed the pre-session check, and the runner said `main` fails), TASK-10014 (echonomicon `TASK-133`: a staged, uncommitted draft with type errors, same wrong message; suggests naming the dirty files and only claiming `main` fails after checking a clean `main`) and TASK-10005 (echonomicon `TASK-213`: a reused worktree had a whitespace-only `chitty.toml` change from an earlier session's formatter, so the move to `review` was refused at handoff; suggests showing the dirty diff in the refusal and reporting pre-existing tracked changes when the session starts). TASK-491 (landed in 0.8.0) now refuses leaving `doing` with a dirty worktree, which removes one cause; the misleading pre-check message remains.

## History

- 2026-11-24T22:21:39Z zesty-coral-newt → backlog
- 2026-11-24T22:21:39Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:33Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:57Z zesty-coral-newt: changed priority
- 2026-11-25T22:32:44Z calm-ochre-quail: changed notes
