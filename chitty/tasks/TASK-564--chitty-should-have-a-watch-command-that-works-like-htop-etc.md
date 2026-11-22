---
title: chitty should have a watch command that works like htop, etc and shows the status of tickets as they change
status: backlog
labels:
  - question
created: 2026-11-22
---

## Description

This ticket needs refining.

## Notes

Suggestion origin: chitty

Question for the owner (2026-11-22, planner): what should the watch view show, and where? Options: (A) `chitty list` redrawn every few seconds, highlighting tickets whose status changed since the last draw; (B) a log-like feed of History lines as they happen (closer to `tail -f`), with the current board at the top; (C) both in one full-screen view. Should it include runner activity (which ticket each `chitty run` is working on, and its phase), or tickets only? Related: `TASK-557` (summary of a recent time window).

## History

- 2026-11-22T09:47:35Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:35Z friendly-jade-stoat: changed notes
- 2026-11-22T10:02:29Z friendly-jade-stoat: changed labels, notes
