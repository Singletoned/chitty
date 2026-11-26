---
title: "Re-check 2026-12-03: stale planner claims block requeuing tickets that workers handed back"
status: backlog
labels:
  - bug
created: 2026-11-26
provisional: true
---

## Description

On 2026-11-26, requeuing seven `planning` tickets (TASK-629, 599, 632, 688, 674, 675, 633) was refused with "TASK-N is being planned by <actor>; leave it alone, or release it with `chitty edit TASK-N -s to-plan --note <reason>`". The named actors were runner workers that had moved the ticket `doing → planning` 1–3 days earlier and then exited. A worker that hands a ticket back is not planning it. Each requeue therefore needed three edits (`to-plan` with a note, then `planning`, then the real edit). Suggested fix: when a worker leaves `doing` for `planning` or `to-plan`, drop its claim, or let a planning claim expire after a set time, for example 12 hours. Also, most of these hand-backs said "no ticket defect"; under the new rules they should be `to-plan` with a decision, or stay `doing`.

## Notes

Suggestion origin: chitty

Mostly addressed since: TASK-10030 tells workers to return tickets to `to-plan`, and TASK-10031 moved old `planning` tickets to `to-plan` on setup upgrade; of the seven tickets named, six are now done. What is left: `claim_refusal` in `src/chitty/model.py` still treats a `doing -> planning` transition as a planning claim.

Decided (the person, 2026-11-26): wait and see; probably a glitch from the move to `to-plan`. Re-check on 2026-12-03: if no `doing -> planning` claim has blocked anyone since 2026-11-26, archive this; otherwise plan option A (only a move into `planning` from `to-plan`, `backlog` or `cold-read` counts as a claim). Chitty has no due dates yet (TASK-619).

## History

- 2026-11-26T18:06:12Z calm-ochre-quail → backlog
- 2026-11-26T18:06:14Z calm-ochre-quail: changed notes
- 2026-11-26T18:07:28Z calm-ochre-quail: changed labels, notes
- 2026-11-26T18:17:06Z calm-ochre-quail: changed notes
- 2026-11-26T18:17:35Z calm-ochre-quail: changed title
