---
title: Mark list lines whose status comes from another branch
status: backlog
depends_on:
  - TASK-602
  - TASK-604
created: 2026-11-23
---

## Description

Decided with the person, 2026-11-23: `chitty list` reads more than one branch and shows a ticket's status from the branch with the newest copy, as it does today, and marks each line whose status comes from another branch, naming that branch. It never refuses because a ticket is out of date here. `chitty next` and `chitty run` keep choosing from those cross-branch statuses, so a running ticket is never mistaken for `todo`.

Depends on `TASK-604` (the once-per-command index of tickets changed on other branches) and `TASK-602`. To be planned: the marker's form (it must fit the existing marker column or the line), `--json`, and tests including a branch behind `main`.

## History

- 2026-11-23T08:22:18Z plucky-umber-wren → todo
- 2026-11-23T08:22:38Z plucky-umber-wren todo → backlog
- 2026-11-23T08:47:34Z plucky-umber-wren: changed title, dependencies, description
