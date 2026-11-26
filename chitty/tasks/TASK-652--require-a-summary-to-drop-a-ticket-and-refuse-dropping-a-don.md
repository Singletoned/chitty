---
title: Require a Summary to drop a ticket, and refuse dropping a `done` one
status: planning
labels:
  - needs-minor
priority: high
depends_on:
  - TASK-599
parent: TASK-599
created: 2026-11-24
---

## Description

`TASK-599` added the `dropped` status, so a ticket nobody will build can be closed without faking a review. Today `chitty edit <id> -s dropped` is accepted from any status with no reason. Decided with the person, 2026-11-22: dropping needs a reason, and a `done` ticket cannot be dropped.

Change, in `Repo._edit_stored` in `src/chitty/store.py`, checked on the task after the edit is applied, before anything is written:

- Resulting status `dropped` and previous status `done`: raise `ChittyError` `<id> is done; it cannot be dropped`.
- Resulting status `dropped` and the Summary section empty after `str.strip()` (missing, `--summary ""`, or whitespace only): raise `ChittyError` `dropping <id> needs a --summary saying why`. This applies to every edit of a dropped ticket, with or without `-s`, so `--note x` on a dropped ticket with no Summary is refused too.

Unchanged: leaving `dropped` for another status; `-s dropped` never needs `review`; no run-lock check.

Tests: add to the existing `tests/test_status_dropped.py` (`CliTestCase`; `RepoTestCase` config has review on). Write `done` and `dropped` fixtures by replacing `status:` in the file, as the existing tests do. Update its `test_edit_to_dropped`, which drops without a Summary. Summary refusals to cover, each asserting the message and a byte-identical file:

- `-s dropped` with no `--summary` on a ticket with no Summary (exits 0 if the ticket already has one);
- `-s dropped --summary ""` on a ticket with a Summary, and `--summary "   "` on one without;
- on a dropped ticket with a Summary: `--summary ""`; on a dropped ticket whose `## Summary` is only blank lines, and one with no Summary: `--note x`.

No property: a fixed set of statuses, all listed.

Out of scope: `chitty add -s dropped` (`TASK-653`), archiving (`TASK-654`), dependents (`TASK-600`).

## Acceptance Criteria

- [ ] From each of `backlog`, `planning`, `cold-read`, `todo`, `doing`, `blocked`, `error` and `review`, `-s dropped --summary "Superseded by TASK-2."` exits 0 and the file has `status: dropped` and that Summary; from `done` it is refused with its message and the file is byte-identical; the `done` case fails before the change
- [ ] Each Summary refusal listed in the Description gives `dropping TASK-1 needs a --summary saying why` and a byte-identical file, and fails before the change; `make check` passes

## History

- 2026-11-24T08:45:25Z sunny-hazel-gannet → planning
- 2026-11-24T08:45:42Z sunny-hazel-gannet: changed description
- 2026-11-26T18:59:24Z zesty-ginger-newt: changed notes
- 2026-11-26T18:59:24Z zesty-ginger-newt planning → to-plan
- 2026-11-26T18:59:33Z zesty-ginger-newt: replaced notes; changed description, acceptance criteria
- 2026-11-26T18:59:33Z zesty-ginger-newt to-plan → planning
- 2026-11-26T18:59:41Z zesty-ginger-newt planning → cold-read
- 2026-11-26T19:01:58Z zesty-ginger-newt cold-read → planning
