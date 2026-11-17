---
title: Archive fails and leaves main dirty while another branch has the active file
status: todo
labels:
  - bug
priority: high
created: 2026-11-17
---

## Description

Seen 2026-11-17 on `main`: `chitty archive TASK-326` and `chitty archive TASK-356` (both `done`) moved the file to `chitty/tasks/archive/`, then failed with "TASK-326 is used by more than one file: chitty/tasks/TASK-326--....md, chitty/tasks/archive/TASK-326--....md" and committed nothing, leaving `main` dirty (` D` active file, `??` archive file). Other worktree branches (for example `task-343`) still hold the active file from an earlier merge of `main`, so the historical copy and the new archived copy count as duplicates. The same dirty state (`TASK-342`, ` D` plus `??`) earlier made `chitty run` fail to land `TASK-326` with "working tree is dirty". Archiving must commit the move even while other branches still have the active file, and a failed archive must not leave the move uncommitted (see `TASK-355`).

## Notes

Also seen 2026-11-17: in the `task-364` worktree, which branched before `TASK-356` was archived on `main`, `chitty edit TASK-364 --note ...` failed with `TASK-356 is used by more than one file` (the local active file and `main`'s archived one), after writing the note to the ticket file and without committing it, despite `TASK-355`. So every worktree created before an archive on `main` cannot edit any ticket until it merges `main`.

## History

- 2026-11-17T19:53:05Z kind-umber-toad → todo
- 2026-11-17T19:59:48Z kind-umber-toad: changed priority, notes
