---
title: Let a repo delete done tasks instead of archiving them
status: doing
labels:
  - cli,config
depends_on:
  - TASK-13
created: 2026-10-26
---

## Description

Some repos will delete done tasks at merge-request time rather than keep an archive; git history is the record. A repo config setting chooses archive (the default) or delete, and chitty archive follows it. No new command.

## Acceptance Criteria

- [ ] In delete mode, chitty archive (with or without an ID) deletes the done task files and reports each one
- [ ] Tests cover delete mode, ID non-reuse and references
- [ ] PLAN.md, README and the agent guide describe it
- [ ] Repo config key archive = "move" | "delete" chooses what chitty archive does; default "move"; any other value is a config error
- [ ] Deleted IDs are never reused: in delete mode the next ID also counts IDs from task files deleted in git history (git log --all --no-renames --diff-filter=D --name-only) and uncommitted deletions (git status --no-renames)
- [ ] If git history is unavailable or shallow in delete mode, creating a task fails with a clear error rather than guessing
- [ ] Deleting a done task removes its ID from other tasks depends_on and reports each change; prose mentions are left alone

## Plan

Await the recorded product decisions before implementing deletion. The implementation will validate the selected retention mode, preserve never-reused IDs, and prevent dangling dependencies according to the owner-approved policy.

## Notes

OPEN QUESTIONS for the human. (1) ID reuse: next ID is max(existing files)+1, so deleting the highest done task would reuse its number. Options: record the high-water mark per context in repo config, or derive it from git history. Recommend the config high-water mark: simple and visible. (2) depends_on pointing at a deleted task is currently a check error. Options: refuse to delete a done task that something still depends on, or strip the reference on delete. Recommend refusing, naming the dependants. (3) Config key name, e.g. done = "archive" | "delete".

HUMAN INPUT NEEDED: Please decide (1) how deleted task numbers are retained: persistent per-context high-water mark in config (recommended) or derive from Git history; (2) what happens when another task depends on a deleted done task: refuse deletion and name dependants (recommended) or strip those references; and (3) confirm the config key/value shape, recommended `done = "archive" | "delete"`.

DECIDED with the human (2026-10-26): (1) derive the highest ID from git history, not a config counter (a counter would conflict on every concurrent MR); the filename already carries the ID, so no format change is needed; (2) strip depends_on references to deleted tasks and report them (a done dependency is already satisfied); (3) config key archive = "move" | "delete", default "move". Supersedes the open questions above. restore and list --archived are being removed separately (TASK-16), so delete mode needs no handling for them.
