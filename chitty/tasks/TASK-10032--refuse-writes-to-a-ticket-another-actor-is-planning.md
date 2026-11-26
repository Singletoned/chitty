---
title: Refuse writes to a ticket another actor is planning
status: doing
depends_on:
  - TASK-10029
parent: TASK-10026
created: 2026-11-25
moved_from: TASK-SYR88D
---

## Description

Part of `TASK-10026`, after `TASK-10029` adds `to-plan`. A planner claims a ticket by moving it to `planning` in the main checkout, then plans on a `plan/` branch and changes the ticket's text only when it has finished. Until then, nothing stops another session editing the same ticket (seen 2026-11-25 on `TASK-676`, where a triage session's edits on `main` forced the planner to redo its work twice).

Rule: a ticket whose status is `planning` is claimed by the actor of its latest `→ planning` entry in `Task.attributed_transitions()` (`src/chitty/model.py`; it skips old date-only History lines, so a ticket with no attributed `→ planning` entry is unclaimed). A write by any other actor is refused, except a release (a move to `to-plan` with a non-blank note, for a claim left by a session that ended) and writes by the actor `human` (`chitty edit --human`), since the person decides.

Change:

- Add a pure function to `src/chitty/model.py`: `claim_refusal(task_id, task, actor, releasing) -> str | None`, returning ``<ID> is being planned by <claimant>; leave it alone, or release it with `chitty edit <ID> -s to-plan --note <reason>` `` when the rule refuses, else `None`.
- In `src/chitty/store.py`, raise `ChittyError` with that message at the top of `Repo._edit_stored`, before any other rule (so `-s done` or `-s review` on a claimed ticket gets this message, not another), with `releasing` true when `edit.status == "to-plan"` and the edit has a non-blank note; at the top of `Repo._set_archived` (archive and restore); and in `Repo.move` for the moved ticket itself (`releasing` is false for both). `Repo.edit_planning` reaches `_edit_stored` with the planner's branch copy, so the claimant's own branch edits pass.

Out of scope, not refused: `renumber`, `renumber_provisional`, `chitty fix`, and reference rewrites in other tickets during `renumber` or `move` (all mechanical); `cold-read`; `chitty run`, which never selects a `planning` ticket; the plan guide (`TASK-10033`).

Tests:

- A Hypothesis property on `claim_refusal` in `tests/test_check_edit.py`, drawing a claimant and another actor (distinct, neither `human`), the status, and `releasing`. For a task whose History ends with `<claimant> backlog → planning`: the claimant and `human` get `None`; the other actor gets a message naming the claimant, or `None` when releasing. With no attributed `→ planning` entry, or any status other than `planning`, every actor gets `None`.
- A CLI example in `tests/test_cli.py`, with the default `archive = "move"`: with `CHITTY_ACTOR=one`, move `TASK-1` to `planning`. With `CHITTY_ACTOR=two`, `chitty note TASK-1 x`, `chitty edit TASK-1 -s done`, `chitty edit TASK-1 -s backlog` and `chitty archive TASK-1` each fail with `being planned by one` and leave the file unchanged; then `chitty edit TASK-1 -s to-plan --note stale` succeeds.

## Acceptance Criteria

- [ ] The property test on `claim_refusal` and the CLI example pass, and each fails before the change
- [ ] `make check` passes

## Plan

Add failing property and CLI tests for planning claims, implement the pure claim rule and enforce it at the specified store write boundaries, then format, run checks, and hand off for review.

## History

- 2026-11-25T23:06:45Z golden-coral-stoat → backlog
- 2026-11-25T23:06:57Z golden-coral-stoat: changed description, acceptance criteria
- 2026-11-25T23:10:11Z golden-coral-stoat: changed description
- 2026-11-25T23:10:13Z golden-coral-stoat: changed acceptance criteria
- 2026-11-25T23:10:43Z golden-coral-stoat: changed description
- 2026-11-25T23:12:17Z golden-coral-stoat: changed description
- 2026-11-25T23:12:30Z golden-coral-stoat backlog → todo
- 2026-11-25T23:12:53Z golden-coral-stoat: renumbered from TASK-SYR88D
- 2026-11-26T02:18:50Z sunny-umber-jay todo → doing
- 2026-11-26T02:21:31Z sunny-umber-jay: wrote the plan
