---
title: chitty should have a watch command that works like htop, etc and shows the status of tickets as they change
status: backlog
created: 2026-11-22
---

## Description

This ticket needs refining.

## Notes

Suggestion origin: chitty

Question for the owner (2026-11-22, planner): what should the watch view show, and where? Options: (A) `chitty list` redrawn every few seconds, highlighting tickets whose status changed since the last draw; (B) a log-like feed of History lines as they happen (closer to `tail -f`), with the current board at the top; (C) both in one full-screen view. Should it include runner activity (which ticket each `chitty run` is working on, and its phase), or tickets only? Related: `TASK-557` (summary of a recent time window).

Owner answer, 2026-11-22: probably like `chitty list`, but including recently done tickets. Owner wonders whether to generalise it into a notify system, for example "notify me when a ticket changes", so nobody has to watch. Planner note: `TASK-557` (summary of a recent time window) and this could share one core: "ticket changes since time T", from History lines. Watch = redraw that; notify = block until it is non-empty, then print and exit (a command an agent can wait on, which would also replace polling in planner sessions).

## History

- 2026-11-22T09:47:35Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:35Z friendly-jade-stoat: changed notes
- 2026-11-22T10:02:29Z friendly-jade-stoat: changed labels, notes
- 2026-11-22T10:28:19Z friendly-jade-stoat: changed labels, notes
