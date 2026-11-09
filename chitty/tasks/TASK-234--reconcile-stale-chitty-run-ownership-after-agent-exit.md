---
title: Reconcile stale `chitty run` ownership after agent exit
status: backlog
created: 2026-11-09
---

## Description

In `chladnify` `TASK-3`, two departed runs left the ticket `blocked` with notes naming supposedly active PIDs (`16653` and `36226`). Neither PID remained in `ps`, and `.worktrees/task-3` was clean, yet `chitty next` returned no work. Have `chitty run` detect child exit and clear or reconcile stale ownership so an otherwise ready ticket returns to `doing` or `review` rather than requiring manual recovery.

## Notes

Suggestion origin: chladnify

## History

- 2026-11-09T12:03:08Z eager-puffin → backlog
- 2026-11-09T12:03:10Z eager-puffin: changed notes
