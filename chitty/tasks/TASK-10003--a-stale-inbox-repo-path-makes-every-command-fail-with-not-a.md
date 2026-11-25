---
title: A stale inbox repo path makes every command fail with Not a directory
status: backlog
labels:
  - bug
created: 2026-11-25
moved_from: TASK-AZ59M3
---

## Description

Observed 2026-11-25. Each project's inbox entry records its repository path in `~/.local/share/chitty/inbox/<project>/repo`. A worker-trial clone was deleted, and a later clone reused the same project name (`chitty-trial-pi152-luna-lean-task-512`). Every command in the new clone, starting with `chitty run`, then failed with `Error: Not a directory: <old deleted path>`, raised by `is_repository` in `src/chitty/git.py:519`.

The new clone was a valid repository with that project name. A recorded path that no longer exists should not be fatal. Either replace it with the current repository, or warn that the old path is gone and carry on. The current error doesn't say that the path came from the inbox, so it is hard to trace. The fix in the trial harness was to delete the inbox entry by hand.

## Notes

Suggestion origin: chitty

Triage 2026-11-25: related to TASK-50 (prune inbox registrations whose repo is gone). The worker-trial harness now avoids it by naming projects after the trial folder (`docs/plan/worker-trials.md`), but the fatal error remains for anyone else.

## History

- 2026-11-25T22:28:31Z calm-ochre-quail → backlog
- 2026-11-25T22:28:33Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:18Z calm-ochre-quail: changed labels, notes
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-AZ59M3
