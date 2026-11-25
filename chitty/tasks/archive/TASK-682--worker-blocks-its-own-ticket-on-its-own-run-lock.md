---
title: Worker blocks its own ticket on its own run lock
status: backlog
labels:
  - bug
created: 2026-11-24
---

## Description

In shelfpath, TASK-6 was set to blocked by actor mellow-dormouse with the note "Chitty reports an active worker (mellow-dormouse, process 24249) running chitty run on this ticket". The lock `.git/chitty/run/TASK-6.lock` was `{"pid": 24249, "actor": "mellow-dormouse", "mode": "work", "started": "2026-11-09T15:54:16Z"}`, and the block was made by the same actor at 15:54:57Z. The agent started by `chitty run` saw its parent run lock and took it for a competing worker. Suggested fixes: tell the spawned agent its own lock or actor (via env var) so it does not report itself as a conflict, and have lock checks treat a lock whose PID is dead as stale. All four shelfpath run locks (TASK-1, 5, 6, 11) are now held by dead PIDs two weeks later.

## Notes

Suggestion origin: shelfpath

Triage 2026-11-24, from TASK-669 (shelfpath): run locks were again left behind after workers exited (PIDs 33747, 6519 and 28502 dead). Related: TASK-234 (guide: leave a ticket alone while another run holds its lock).

Archived 2026-11-25, already fixed: 7ed917e1 (2026-11-10, a day after the shelfpath report) marks a run lock as the worker's own in chitty show via CHITTY_ACTOR (locks.holder, field you). Locks are flock-held, so a dead PID never holds one; leftover lock files are inert.

## History

- 2026-11-24T22:21:45Z zesty-coral-newt → backlog
- 2026-11-24T22:21:45Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:58Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:51Z zesty-coral-newt: changed labels
- 2026-11-25T20:46:41Z golden-coral-stoat: changed notes
- 2026-11-25T20:46:52Z golden-coral-stoat backlog → archived
