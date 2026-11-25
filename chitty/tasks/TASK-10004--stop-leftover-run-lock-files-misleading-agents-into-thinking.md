---
title: Stop leftover run lock files misleading agents into thinking a run is active
status: backlog
created: 2026-11-25
moved_from: TASK-C8F9DY
---

## Description

On 2026-11-24 a triage session left TASK-671 and TASK-681 open because their targets (TASK-233, TASK-599) 'have branches with run locks held'. Neither lock was held: locks are flock-based (src/chitty/locks.py), and both lock files named dead PIDs (6392, 62280). .git/chitty/run/ holds about 300 inert lock files, so an agent that lists that directory or cats a file is easily misled. Options: remove the lock file when a run releases it, or have chitty show / chitty list say plainly whether a run is active (show already reports 'running' via locks.holder), and say in the plan guide to rely on that instead of the lock files.

## Notes

Suggestion origin: chitty

## History

- 2026-11-25T22:28:30Z calm-ochre-quail → backlog
- 2026-11-25T22:28:31Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:25Z calm-ochre-quail: changed title
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-C8F9DY
