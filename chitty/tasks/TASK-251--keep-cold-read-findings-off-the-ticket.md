---
title: Keep cold-read findings off the ticket
status: backlog
created: 2026-11-10
---

## Description

Readers see earlier reads' findings in Notes, which likely biases them, and per-read notes bloat tickets that workers read.

Change the guides in `src/chitty/roles/`:

- `cold-read.md` (line 9): read only the Description and Acceptance Criteria; skip Notes, which may hold earlier reads' findings.
- `plan.md` (line 26): fix or reject each finding in the ticket text, and give the outcomes in your reply, not in a ticket note.
- `plan.md` (line 29): drop the "replace its notes once reads converge" bullet; with no per-read notes there is nothing to replace.
- Keep the one note `plan.md` allows at line 42, pointing the worker at a kept read as a starting point.

Put the tests in `tests/test_guide_cold_read_notes.py`, checking the printed guides (`chitty guide cold-read TASK-1`, `chitty guide plan`). Update `PLAN.md` where it describes recording outcomes.

## Acceptance Criteria

- [ ] `chitty guide cold-read <ID>` tells the reader to skip Notes, and `chitty guide plan` says to give finding outcomes in the reply, not a ticket note.
- [ ] `chitty guide plan` no longer tells planners to replace notes once reads converge, and still describes the starting-point note.

## History

- 2026-11-10T21:58:44Z jolly-heron → backlog
