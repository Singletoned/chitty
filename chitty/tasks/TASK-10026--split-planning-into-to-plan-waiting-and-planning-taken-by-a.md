---
title: Split `planning` into `to-plan` (waiting) and `planning` (taken by a planner)
status: backlog
labels:
  - bug
  - needs-minor
created: 2026-11-25
---

## Description

Seen 2026-11-25: a planner on `plan/backlog-2026-11-25` was rewriting `TASK-676` while a triage session edited the same ticket on `main` twice and a renumber rewrote IDs in its notes. Nothing told either session about the other; the planner had to reset its branch and resolve conflicts on the ticket file by hand, twice.

Cause: `planning` means both "waiting for a planner" and "a planner has it", so no session can tell a taken ticket from a waiting one. A planner changes a ticket's text only when it has finished planning, so the ticket's Git history cannot show the claim either.

Decided with the person, 2026-11-25:

- `to-plan`: waiting for a planner, the counterpart of `todo`. Workers and reviewers return tickets here.
- `planning`: taken, the counterpart of `doing`. A planner claims a ticket by moving it to `planning` in the main checkout, plans on a `plan/` branch, and lands it. Other actors' writes to it are refused, except a release to `to-plan` with a note and edits by `human`.
- `backlog` stays separate; planners take `to-plan` tickets first.
- Existing `planning` tickets move to `to-plan` once, when repository setup upgrades.

Children, in order: `TASK-10029` (add `to-plan`, send returns there), `TASK-10030` (guide, prompt and doc wording), `TASK-10032` (refuse other actors' writes to a `planning` ticket), `TASK-10031` (migrate on setup upgrade), `TASK-10033` (plan guide). Separate but related: `TASK-10028` (rename `todo` to `to-do`) and `TASK-599` (`dropped`), which also change the status set; `TASK-340`, which this claim makes safer.

This ticket is done when its children are.

## History

- 2026-11-25T22:56:40Z golden-coral-stoat → backlog
- 2026-11-25T23:00:49Z golden-coral-stoat: changed title, labels, description
- 2026-11-25T23:08:29Z golden-coral-stoat: changed description
- 2026-11-25T23:13:07Z golden-coral-stoat: changed description
