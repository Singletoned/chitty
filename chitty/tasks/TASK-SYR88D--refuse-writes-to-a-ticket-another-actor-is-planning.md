---
title: Refuse writes to a ticket another actor is planning
status: backlog
depends_on:
  - TASK-B7CQGM
parent: TASK-10026
created: 2026-11-25
provisional: true
---

## Description

Part of `TASK-10026`, after `TASK-B7CQGM` adds `to-plan`. A planner claims a ticket by moving it to `planning` in the main checkout, then plans on a `plan/` branch and changes the ticket's text only when it has finished. Until then, nothing stops another session editing the same ticket (seen 2026-11-25 on `TASK-676`, where a triage session's edits on `main` forced the planner to redo its work twice).

Rule: a ticket whose status is `planning` is claimed by the actor of its latest `→ planning` entry in `Task.attributed_transitions()` (`src/chitty/model.py`; it skips old date-only History lines, so a ticket with no attributed `→ planning` entry is unclaimed). A write by any other actor is refused, except a release (a move to `to-plan` with a non-blank note, for a claim left by a session that ended) and writes by the actor `human` (`chitty edit --human`), since the person decides.

Change:

- Add a pure function to `src/chitty/model.py`: `claim_refusal(task, actor, releasing) -> str | None`, returning `<ID> is being planned by <claimant>; leave it alone, or release it with \`chitty edit <ID> -s to-plan --note <reason>\`` when the rule refuses, else `None`. (`<ID>` may need passing in, or format the message at the call site.)
- In `src/chitty/store.py`, raise `ChittyError` with that message at the top of `Repo._edit_stored`, before any other rule (so `-s done` or `-s review` on a claimed ticket gets this message, not another), with `releasing` true when `edit.status == "to-plan"` and the edit has a non-blank note; at the top of `Repo._set_archived` (archive and restore); and in `Repo.move` for the moved ticket itself.

Out of scope, not refused: `renumber`, `renumber_provisional`, `chitty fix`, and reference rewrites in other tickets during `renumber` or `move` (all mechanical); `cold-read`; `chitty run`, which never selects a `planning` ticket; the plan guide (`TASK-WWNDDM`).

Tests:

- A Hypothesis property on `claim_refusal` in `tests/test_check_edit.py`, drawing a claimant and another actor (distinct, neither `human`), the status, and `releasing`. For a task whose History ends with `<claimant> backlog → planning`: the claimant and `human` get `None`; the other actor gets a message naming the claimant, or `None` when releasing. With no attributed `→ planning` entry, or any status other than `planning`, every actor gets `None`.
- A CLI example in `tests/test_cli.py`: with `CHITTY_ACTOR=one`, move `TASK-1` to `planning`. With `CHITTY_ACTOR=two`, `chitty note TASK-1 x`, `chitty edit TASK-1 -s done`, `chitty edit TASK-1 -s backlog` and `chitty archive TASK-1` each fail with `being planned by one` and leave the file unchanged; then `chitty edit TASK-1 -s to-plan --note stale` succeeds.

## Acceptance Criteria

- [ ] The property test in `tests/test_check_edit.py` and the CLI example in `tests/test_cli.py` pass, and each fails before the change
- [ ] `make check` passes

## History

- 2026-11-25T23:06:45Z golden-coral-stoat → backlog
- 2026-11-25T23:06:57Z golden-coral-stoat: changed description, acceptance criteria
- 2026-11-25T23:10:11Z golden-coral-stoat: changed description
