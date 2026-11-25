---
title: Runner check error blames main when the worktree has uncommitted work
status: backlog
created: 2026-11-25
provisional: true
---

## Description

In echonomicon, TASK-133 went to error with the note: 'Runner error (check): check exited with status 2; output in .chitty/check.log; the branch has no work yet, so main fails this check'. But main passes the check (make lint exits 0 on main). The failure came from a staged but uncommitted file in the ticket worktree (.worktrees/task-133: 'A src/echonomicon/key_registry.py', a worker's draft with 4 ty errors). The runner decided 'the branch has no work yet' from the commit history alone and told readers main is broken, which sends triage the wrong way. Suggest: when the branch has no commits beyond main, check git status in the worktree too; if there are uncommitted changes, say the failure may come from them and name the files, and only claim main fails after running the check on a clean main checkout.

## Notes

Suggestion origin: echonomicon

Triage 2026-11-25: merged into TASK-676.

## History

- 2026-11-25T22:28:35Z calm-ochre-quail → backlog
- 2026-11-25T22:28:36Z calm-ochre-quail: changed notes
- 2026-11-25T22:33:39Z calm-ochre-quail: changed notes
- 2026-11-25T22:33:42Z calm-ochre-quail backlog → archived
