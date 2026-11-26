---
title: "Work guide: suggest small unrelated work instead of adding tickets on a ticket branch"
status: review
labels:
  - untestable
owner: human
created: 2026-11-23
---

## Description

Change `src/chitty/roles/work.md`. In its last bullet, replace `File unrelated work with chitty add (or -c human, or chitty suggest PROJECT)` with: file something unrelated with `chitty suggest` when it is small, and return this ticket to `to-plan` when it is big; do not add tickets on a ticket branch. (In the 30 days to 2026-11-23, none of 419 ticket adds on `main` came from another ticket's branch.) Keep the advice general, because the guides reach every repository.

Size: the guide stays the same length.

Dropped on 2026-11-26: one line in each role guide on rebasing after an out-of-date warning. The warning from TASK-602 and TASK-10040 now says so itself (`...; merge or rebase it now and resolve any conflict`), so the guides need no text.

## Plan

Replace the unrelated-work sentence in the last bullet of `src/chitty/roles/work.md` to direct small unrelated work to `chitty suggest`, big unrelated work to `to-plan`, and forbid adding tickets on a ticket branch, keeping the bullet at 2 lines and general. Verify with `make check` via `chitty edit -s review`.

## Summary

Updated the last bullet of `src/chitty/roles/work.md` to direct small unrelated work to `chitty suggest`, big unrelated work to `to-plan`, and forbid adding tickets on a ticket branch, keeping the bullet at 2 lines (same length) and general:

- Leave `human` tickets in `todo`. Do not do unrelated work: `chitty suggest`
  if small, return to `to-plan` if big; never add tickets on a ticket branch.

Branch `task-605` (worktree `.worktrees/task-605`). `make check` passed via `chitty edit -s review`.

## History

- 2026-11-23T08:47:14Z plucky-umber-wren → backlog
- 2026-11-25T23:50:22Z calm-ochre-quail: changed labels, owner, description
- 2026-11-25T23:50:22Z calm-ochre-quail backlog → todo
- 2026-11-26T10:55:31Z tidy-silver-puffin todo → doing
- 2026-11-26T10:55:42Z tidy-silver-puffin: changed owner
- 2026-11-26T10:55:42Z tidy-silver-puffin doing → todo
- 2026-11-26T18:02:21Z brisk-bronze-adder: changed title, dependencies, description
- 2026-11-26T18:17:03Z calm-russet-badger: wrote the plan
- 2026-11-26T18:17:03Z calm-russet-badger todo → doing
- 2026-11-26T18:33:51Z calm-russet-badger: changed owner, summary
- 2026-11-26T18:33:51Z calm-russet-badger doing → review
