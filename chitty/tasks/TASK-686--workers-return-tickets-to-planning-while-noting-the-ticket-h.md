---
title: Workers return tickets to planning while noting the ticket has no defect
status: backlog
created: 2026-11-24
---

## Description

Seen 2026-11-24 under `chitty run`: within about 3 minutes of claiming a ticket, a worker moved it `doing -> planning` with a note saying there is no ticket defect. `TASK-629` (09:22 to 09:25Z, actor `sunny-khaki-crane`): "Ticket is implementable and no defect or external obstacle has been identified; implementation remains unfinished." `TASK-651` (09:09 to 09:17Z, `honest-hazel-dormouse`): "No ticket defect identified; returning to planning is not appropriate under the status rules", yet it returned it anyway, leaving uncommitted edits in `.worktrees/task-651`. `TASK-629` had already been returned on 2026-11-23 for "execution budget". Each return costs a planner session to requeue. Possible fixes: have the worker guide say that an unfinished but sound ticket stays in `doing` (the runner continues it); or have `chitty edit -s planning` from `doing` require a note naming a planning blocker. Check also which `work_model` these sessions ran on.

## Notes

Suggestion origin: chitty

Triage 2026-11-24: merged the echonomicon reports of the same problem (gpt-6-luna under `chitty run --loop --mode work`). This ticket now holds the "worker returns a sound ticket to planning" part; leftover uncommitted edits are TASK-676, and stall detection is TASK-585.

- TASK-670: TASK-197's worker noted "Returning to planning is not appropriate: requirements are actionable; continue." and then set planning. TASK-196 went to planning over missing tests, an implementation gap.
- TASK-677: TASK-217 and TASK-219 got an implementation commit and no tests, then went to planning with "please resume implementation with those tests". TASK-213 went twice over a question the ticket already answered. Ideas: the work guide says a missing piece of one's own work is never a planning blocker; refuse a planning return whose branch touches `src/` but not `tests/` when the criteria name tests; tell workers to write the tests first.
- TASK-687: TASK-203's note was "Implementation has not started. The ticket is actionable and does not have a discovered defect". The runner's continuation prompt ("finish it ..., return it to planning for a defect..., or set it to blocked") seems to push the worker into picking planning. Suggestion: when a doing->planning note denies a defect, or no ticket text changed, treat the session as failed (todo or retry) instead.
- TASK-656: same evidence (TASK-195, 196, 197, 202, 203), plus a request to compare luna and terra sessions on the same tickets. Pi session logs are under `~/.pi/agent/sessions/--Users-singletoned-src-singletoned-echonomicon-.worktrees-task-<n>--/`.

## History

- 2026-11-24T22:21:48Z zesty-coral-newt → backlog
- 2026-11-24T22:21:49Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:31Z zesty-coral-newt: changed notes
