---
title: Worker blocks its own ticket on its own run lock
status: backlog
created: 2026-11-24
---

## Description

In shelfpath, TASK-6 was set to blocked by actor mellow-dormouse with the note "Chitty reports an active worker (mellow-dormouse, process 24249) running chitty run on this ticket". The lock `.git/chitty/run/TASK-6.lock` was `{"pid": 24249, "actor": "mellow-dormouse", "mode": "work", "started": "2026-11-09T15:54:16Z"}`, and the block was made by the same actor at 15:54:57Z. The agent started by `chitty run` saw its parent run lock and took it for a competing worker. Suggested fixes: tell the spawned agent its own lock or actor (via env var) so it does not report itself as a conflict, and have lock checks treat a lock whose PID is dead as stale. All four shelfpath run locks (TASK-1, 5, 6, 11) are now held by dead PIDs two weeks later.

## Notes

Suggestion origin: shelfpath

## History

- 2026-11-24T22:21:45Z zesty-coral-newt → backlog
- 2026-11-24T22:21:45Z zesty-coral-newt: changed notes
