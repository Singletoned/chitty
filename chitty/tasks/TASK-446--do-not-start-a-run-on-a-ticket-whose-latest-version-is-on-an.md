---
title: Do not start a run on a ticket whose latest version is on another branch
status: backlog
created: 2026-11-19
---

## Description

On 2026-11-13 a hand-run session promoted `BACKLOG-93769170` to TASK-319, set it to `doing` and implemented it (`14670e2`), all on a branch it named `backlog-93769170` in `../chitty-review-completeness`, never on `main`. Two minutes later `chitty run` saw TASK-319 in `doing` (Chitty reads tickets across branches), made a fresh `task-319` from `main`, started an agent, and recorded `error`: "TASK-319 was unchanged". The planner merged the work in by hand on 2026-11-14. Chitty already detects this case for `chitty edit` ("latest committed version is on branch task-321; run Chitty in worktree ..."). Suggest: `chitty next`/`chitty run` skip, or refuse with that same message, any ticket whose latest version is on a branch other than `task-<id>`, instead of creating a new branch. Optionally the work guide could tell hand-run sessions to name their branch `task-<id>`.

## Notes

Suggestion origin: chitty

Planner, 2026-11-19: held, not planned. The ticket-state migration (`TASK-378`, `TASK-385`, `TASK-386`) reads each ticket only from `task-<n>` or `main`; `TASK-386` deletes `git.historical_files`, the cross-branch scan that let `chitty run` see `TASK-319` as `doing` from branch `backlog-93769170`. After that the runner cannot see a ticket on an unconventionally named branch, so this bug should disappear. Re-check once `TASK-386` is done, then archive or plan.

## History

- 2026-11-19T20:55:19Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:20Z sunny-white-dormouse: changed notes
- 2026-11-19T21:21:17Z sunny-white-dormouse: changed notes
