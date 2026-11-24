---
title: Workers return tickets to planning while noting the ticket has no defect
status: backlog
created: 2026-11-24
---

## Description

Seen 2026-11-24 under `chitty run`: within about 3 minutes of claiming a ticket, a worker moved it `doing -> planning` with a note saying there is no ticket defect. `TASK-629` (09:22 to 09:25Z, actor `sunny-khaki-crane`): "Ticket is implementable and no defect or external obstacle has been identified; implementation remains unfinished." `TASK-651` (09:09 to 09:17Z, `honest-hazel-dormouse`): "No ticket defect identified; returning to planning is not appropriate under the status rules", yet it returned it anyway, leaving uncommitted edits in `.worktrees/task-651`. `TASK-629` had already been returned on 2026-11-23 for "execution budget". Each return costs a planner session to requeue. Possible fixes: have the worker guide say that an unfinished but sound ticket stays in `doing` (the runner continues it); or have `chitty edit -s planning` from `doing` require a note naming a planning blocker. Check also which `work_model` these sessions ran on.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:48Z zesty-coral-newt → backlog
- 2026-11-24T22:21:49Z zesty-coral-newt: changed notes
