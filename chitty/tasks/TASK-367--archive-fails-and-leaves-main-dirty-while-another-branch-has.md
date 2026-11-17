---
title: Archive fails and leaves main dirty while another branch has the active file
status: todo
labels:
  - bug
created: 2026-11-17
---

## Description

Seen 2026-11-17 on `main`: `chitty archive TASK-326` and `chitty archive TASK-356` (both `done`) moved the file to `chitty/tasks/archive/`, then failed with "TASK-326 is used by more than one file: chitty/tasks/TASK-326--....md, chitty/tasks/archive/TASK-326--....md" and committed nothing, leaving `main` dirty (` D` active file, `??` archive file). Other worktree branches (for example `task-343`) still hold the active file from an earlier merge of `main`, so the historical copy and the new archived copy count as duplicates. The same dirty state (`TASK-342`, ` D` plus `??`) earlier made `chitty run` fail to land `TASK-326` with "working tree is dirty". Archiving must commit the move even while other branches still have the active file, and a failed archive must not leave the move uncommitted (see `TASK-355`).

## History

- 2026-11-17T19:53:05Z kind-umber-toad → todo
