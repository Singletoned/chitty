---
title: Land waiting tickets at the start of `chitty run`
status: todo
priority: medium
depends_on:
  - TASK-151
parent: TASK-106
created: 2026-11-04
---

## Description

Last part of landing, after `TASK-131`, so a ticket whose landing failed or was interrupted still lands.

A pending ticket is a non-archived `done` ticket with a local branch named `<id in lower case>`. Find it by branch name, not `StoredTask.branch`, which is `None` once the file matches `main`. Legacy branches with other names are ignored, and remote refs are never touched. If the branch has no worktree, add one as in `TASK-126`.

At the start of every `chitty run`, before selecting a ticket, land each pending ticket in ID order, stopping at the first failure. Read statuses through `Repo.find`, which sees the newest copy on any branch. A run naming a ticket, from `TASK-138`, skips this, because it should touch only that ticket. A landing failure now gets another try here, which `TASK-131` could not offer. Every step is a no-op once done, so a later run repeats only what is left.

A successful landing here ends that run, printing what landed and exiting 0: the running process still holds the old code, so the next agent must start from a new `chitty run`, which refreshes setup first. A failure also stops the run, exiting non-zero. This overrides the `TASK-124` rule that a changed status exits 0, so update its tests where needed.

Out of scope: pushing.

## Acceptance Criteria

- [ ] Tests show two pending tickets landing in ID order and a stop at the first failure
- [ ] Tests show a leftover unfinished rebase stopping loudly, and a retry completing after a failed worktree removal
- [ ] A test shows a landing at the start of a run exiting 0 without starting the agent, and the next run selecting a ticket
- [ ] A test shows a landing that failed being completed by a later run once its cause is fixed

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Fixed: where this runs, how it reads status, and `--ticket`; took over "a later run lands it" from `TASK-131`. Rejected: an order against `TASK-136` and the others changing `src/chitty/run.py`, because one ticket is in work at a time, and each rebases on what has landed.

## History

- 2026-11-04T15:11:36Z mellow-newt → todo
- 2026-11-04T15:17:40Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-05T10:07:35Z mellow-newt: changed description
