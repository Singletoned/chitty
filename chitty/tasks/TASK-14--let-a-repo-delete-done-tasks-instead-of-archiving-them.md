---
title: Let a repo delete done tasks instead of archiving them
status: todo
labels:
  - cli,config
depends_on:
  - TASK-13
created: 2026-10-26
---

## Description

Some repos will delete done tasks at merge-request time rather than keep an archive; git history is the record. A repo config setting chooses archive (the default) or delete, and chitty archive follows it. No new command.

## Acceptance Criteria

- [ ] A repo config key chooses archive or delete for done tasks; default archive; an unknown value is a config error
- [ ] In delete mode, chitty archive (with or without an ID) deletes the done task files and reports each one
- [ ] Deleted IDs are never reused: next ID allocation still accounts for them
- [ ] depends_on references to deleted tasks are handled (see open questions)
- [ ] Tests cover delete mode, ID non-reuse and references
- [ ] PLAN.md, README and the agent guide describe it

## Notes

OPEN QUESTIONS for the human. (1) ID reuse: next ID is max(existing files)+1, so deleting the highest done task would reuse its number. Options: record the high-water mark per context in repo config, or derive it from git history. Recommend the config high-water mark: simple and visible. (2) depends_on pointing at a deleted task is currently a check error. Options: refuse to delete a done task that something still depends on, or strip the reference on delete. Recommend refusing, naming the dependants. (3) Config key name, e.g. done = "archive" | "delete".
