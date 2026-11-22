---
title: "`chitty add` files new tickets in `todo`, which planners must remember to undo"
status: backlog
created: 2026-11-22
---

## Description

Seen 2026-11-22: a planner split a follow-up with `chitty add ... -d ...` (no criteria, meant for `backlog`), and the ticket landed in `todo`, where `chitty run` would pick it up. `chitty add --help` says "Create a task with status todo", and `chitty guide plan` says "Keep a new ticket in backlog until you start writing it", so every planner has to follow each add with `chitty edit -s backlog`. Options: an `add -s/--status` option; or refuse `add` into `todo` without acceptance criteria (unless labelled `untestable`); or default to `backlog` when there are no criteria. The last would have prevented this with no new option.

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T13:16:26Z friendly-jade-stoat → backlog
- 2026-11-22T13:16:26Z friendly-jade-stoat: changed notes
