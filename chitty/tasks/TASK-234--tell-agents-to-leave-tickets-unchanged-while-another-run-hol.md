---
title: Tell agents to leave tickets unchanged while another run holds the lock
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-09
---

## Description

In Chladnify TASK-3, agents manually moved a ticket to `blocked` twice because another live `chitty run` held it (PIDs 16653 and 36226). When the other runs ended, the kernel released their locks, but the explicit blocked status remained and required human recovery. This is not stale runner ownership: TASK-200 already releases run locks on exit. Update `chitty guide work` and `chitty guide review` to tell manually started agents who find another active Chitty run on the same ticket not to edit its files or status, especially not to set `blocked` solely for that transient lock. Stop and let the operator retry after that run finishes. Preserve `blocked` for real human-intervention problems; do not make the runner clear blocked tickets automatically. Out of scope: changing locking or `chitty run` behavior.

## Acceptance Criteria

- [ ] Dedicated fail-first guide tests show both `chitty guide work` and `chitty guide review` tell agents to leave the ticket and status unchanged when another run holds its lock, and to retry after release rather than mark it blocked.
- [ ] The existing rules for actual human-intervention blocks remain intact, and `make check` passes.

## Notes

Suggestion origin: chladnify

Triage against the Chladnify TASK-3 history: the ticket was explicitly moved to blocked by agents when they saw another live chitty run PID, and explicitly unblocked by a human after the processes ended. Chitty did not leave a stale kernel lock or automatically mark the ticket blocked; TASK-200 already releases flock locks on process exit. Automatically clearing any blocked ticket after an agent exits would erase genuine human-intervention blocks. Pending a decision on whether to add guide instructions not to set blocked solely for another live run, or close as a manual-session misuse.

Decision from the user: guide-only fix, not automatic unblock. The imported description misattributed two manual blocked transitions in Chladnify TASK-3 to stale ownership after child exit; the ticket was explicitly blocked by agents while other PIDs were alive. Replaced scope accordingly; backlog pending implementing cold read.

## History

- 2026-11-09T12:03:08Z eager-puffin → backlog
- 2026-11-09T12:03:10Z eager-puffin: changed notes
- 2026-11-09T12:04:58Z eager-puffin: changed owner, notes
- 2026-11-09T12:07:36Z eager-puffin: changed title, priority, owner, parent, description, acceptance criteria, notes
