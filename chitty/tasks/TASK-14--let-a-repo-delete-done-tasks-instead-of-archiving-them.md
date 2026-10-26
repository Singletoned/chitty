---
title: Let a repo delete done tasks instead of archiving them
status: done
labels:
  - cli,config
depends_on:
  - TASK-13
created: 2026-10-26
---

## Description

Some repos will delete done tasks at merge-request time rather than keep an archive; git history is the record. A repo config setting chooses archive (the default) or delete, and chitty archive follows it. No new command.

## Acceptance Criteria

- [x] In delete mode, chitty archive (with or without an ID) deletes the done task files and reports each one
- [x] Tests cover delete mode, ID non-reuse and references
- [x] PLAN.md, README and the agent guide describe it
- [x] Repo config key archive = "move" | "delete" chooses what chitty archive does; default "move"; any other value is a config error
- [x] Deleted IDs are never reused: in delete mode the next ID also counts IDs from task files deleted in git history (git log --all --no-renames --diff-filter=D --name-only) and uncommitted deletions (git status --no-renames)
- [x] If git history is unavailable or shallow in delete mode, creating a task fails with a clear error rather than guessing
- [x] Deleting a done task removes its ID from other tasks depends_on and reports each change; prose mentions are left alone

## Plan

Implement the decided archive retention setting (`archive = "move" | "delete"`). In delete mode, derive allocated IDs from current files, committed deletion history, and working-tree deletions; strip exact depends_on entries and include those rewrites in the one finalization/autocommit.

## Notes

OPEN QUESTIONS for the human. (1) ID reuse: next ID is max(existing files)+1, so deleting the highest done task would reuse its number. Options: record the high-water mark per context in repo config, or derive it from git history. Recommend the config high-water mark: simple and visible. (2) depends_on pointing at a deleted task is currently a check error. Options: refuse to delete a done task that something still depends on, or strip the reference on delete. Recommend refusing, naming the dependants. (3) Config key name, e.g. done = "archive" | "delete".

HUMAN INPUT NEEDED: Please decide (1) how deleted task numbers are retained: persistent per-context high-water mark in config (recommended) or derive from Git history; (2) what happens when another task depends on a deleted done task: refuse deletion and name dependants (recommended) or strip those references; and (3) confirm the config key/value shape, recommended `done = "archive" | "delete"`.

DECIDED with the human (2026-10-26): (1) derive the highest ID from git history, not a config counter (a counter would conflict on every concurrent MR); the filename already carries the ID, so no format change is needed; (2) strip depends_on references to deleted tasks and report them (a done dependency is already satisfied); (3) config key archive = "move" | "delete", default "move". Supersedes the open questions above. restore and list --archived are being removed separately (TASK-16), so delete mode needs no handling for them.

Decision acknowledged: use git deletion history plus uncommitted deletions for ID allocation, strip exact depends_on entries while reporting rewrites, and configure `archive = "move" | "delete"` (default move). Proceeding with implementation.

Verified: archive=move|delete is validated and defaults to move. Delete mode removes done files, strips and reports exact dependencies, derives never-reused IDs from committed and working-tree deletions, and fails on unavailable history. Documentation and full make check pass.
