---
title: Split `planning` into `to-plan` (waiting) and `planning` (taken by a planner)
status: backlog
labels:
  - bug
  - needs-minor
created: 2026-11-25
---

## Description

Seen 2026-11-25: a planner on `plan/backlog-2026-11-25` was rewriting `TASK-676` while a triage session (`calm-ochre-quail`) edited the same ticket on `main` twice and a renumber rewrote IDs in its notes. Nothing told either session about the other; the planner had to reset its branch and resolve rename/modify conflicts on the ticket file by hand, twice.

Cause: `planning` means both "waiting for a planner" and "a planner is working on it", so no session can tell a taken ticket from a waiting one (on 2026-11-25, 20 tickets were `planning` and one had an owner). A planner changes the ticket's text only once it has finished planning, so the ticket's Git history cannot show the claim either.

Decided with the person, 2026-11-25:

- New status `to-plan`: waiting for a planner, the counterpart of `todo`, with no owner. Workers and reviewers return tickets here instead of `planning`.
- `planning` now means taken: the counterpart of `doing`. A planner sets it, with `owner` set to its actor, on `main` in one commit before branching. While a ticket is `planning` with an owner, writes to it from other actors refuse, naming the owner; `chitty run` and `chitty next` skip it. Finishing (`cold-read` or `todo`) or handing back (`to-plan`) clears the owner.
- `backlog` stays separate: suggestions nobody has decided to do. Planners take `to-plan` tickets before `backlog`.
- `chitty fix` moves existing `planning` tickets with no owner to `to-plan`.

To settle while planning, then split into several tickets: the status order and allowed moves in `src/chitty/model.py` and `store.py` (`returning_to_planning`, `TASK-10000`'s repeated-return count), the migration, the guides and runner prompts, how a planner's claim commit on `main` fits `TASK-340`, and planning it together with `TASK-599` (`dropped`) and the `to-do` rename (`TASK-KD5X8V`), since all three change the status set.

## History

- 2026-11-25T22:56:40Z golden-coral-stoat → backlog
- 2026-11-25T23:00:49Z golden-coral-stoat: changed title, labels, description
