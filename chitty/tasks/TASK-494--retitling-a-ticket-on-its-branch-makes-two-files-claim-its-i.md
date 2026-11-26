---
title: Retitling a ticket on its branch makes two files claim its ID
status: backlog
created: 2026-11-21
---

## Description

Seen 2026-11-20: `chitty edit TASK-276 --title ...` in worktree `.worktrees/task-276` renamed the ticket file on branch `task-276` (new slug), while `main` kept the old file name. Every Chitty write in the main checkout then failed: `chitty run` stopped with "cannot finalize task write with unresolved problems: ... TASK-276 is used by more than one file: <old name>, <new name>". Renaming the stale `main` copy to the new name (commit `8d03505c`) cleared the error but made Chitty read the stale `main` copy as current (old title, old design, status `doing`) instead of the branch copy, until the branch text was copied to `main` (next commit). Two fixes to consider: treat files on different refs with the same ID as one ticket placement when choosing the authoritative copy (related: `TASK-378`, `TASK-367`); and do not rename a ticket file when its title changes on a ticket branch, deferring the slug change until it lands.

## Notes

Suggestion origin: chitty

Triage 2026-11-26: not covered by TASK-602 or TASK-10040.

## History

- 2026-11-21T07:57:57Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:58Z nimble-umber-gannet: changed notes
- 2026-11-26T18:02:43Z brisk-bronze-adder: changed notes
