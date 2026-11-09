---
title: Reconcile stale `chitty run` ownership after agent exit
status: backlog
owner: human
created: 2026-11-09
---

## Description

In `chladnify` `TASK-3`, two departed runs left the ticket `blocked` with notes naming supposedly active PIDs (`16653` and `36226`). Neither PID remained in `ps`, and `.worktrees/task-3` was clean, yet `chitty next` returned no work. Have `chitty run` detect child exit and clear or reconcile stale ownership so an otherwise ready ticket returns to `doing` or `review` rather than requiring manual recovery.

## Notes

Suggestion origin: chladnify

Triage against the Chladnify TASK-3 history: the ticket was explicitly moved to blocked by agents when they saw another live chitty run PID, and explicitly unblocked by a human after the processes ended. Chitty did not leave a stale kernel lock or automatically mark the ticket blocked; TASK-200 already releases flock locks on process exit. Automatically clearing any blocked ticket after an agent exits would erase genuine human-intervention blocks. Pending a decision on whether to add guide instructions not to set blocked solely for another live run, or close as a manual-session misuse.

## History

- 2026-11-09T12:03:08Z eager-puffin → backlog
- 2026-11-09T12:03:10Z eager-puffin: changed notes
- 2026-11-09T12:04:58Z eager-puffin: changed owner, notes
