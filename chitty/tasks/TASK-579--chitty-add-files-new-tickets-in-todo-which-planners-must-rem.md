---
title: "`chitty add` files new tickets in `todo`, which planners must remember to undo"
status: backlog
labels:
  - question
created: 2026-11-22
---

## Description

Seen 2026-11-22: a planner split a follow-up with `chitty add ... -d ...` (no criteria, meant for `backlog`), and the ticket landed in `todo`, where `chitty run` would pick it up. `chitty add --help` says "Create a task with status todo", and `chitty guide plan` says "Keep a new ticket in backlog until you start writing it", so every planner has to follow each add with `chitty edit -s backlog`. Options: an `add -s/--status` option; or refuse `add` into `todo` without acceptance criteria (unless labelled `untestable`); or default to `backlog` when there are no criteria. The last would have prevented this with no new option.

## Notes

Suggestion origin: chitty

Question for the owner (2026-11-22, planner): `chitty add` creates tickets in `todo`, where `chitty run` can pick them up before anyone has planned them. Which fix do you want? (A) Recommended: `add` creates tickets in `backlog` unless they have acceptance criteria (`--ac`), with no new option; a human's quick `chitty add "..."` then waits in backlog. (B) `add` always creates in `backlog`, and `-s todo` (new option) puts it straight in todo. (C) Leave `add` as it is and refuse `todo` without criteria, unless labelled `untestable`. A, B and C all change default behaviour, so the ticket gets `needs-minor`.

## History

- 2026-11-22T13:16:26Z friendly-jade-stoat → backlog
- 2026-11-22T13:16:26Z friendly-jade-stoat: changed notes
- 2026-11-22T13:19:01Z friendly-jade-stoat: changed labels, notes
