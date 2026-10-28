---
title: Keep task filenames in step with titles
status: todo
created: 2026-10-28
---

## Description

Filenames are <ID>--<slug>.md, but the slug is fixed when the task is created, so after a title edit the filename stops describing the task (e.g. TASK-40). Filenames should broadly reflect titles: rename the file when the title changes, and have chitty fix repair stale slugs in existing tasks. The ID stays the identity, so references are unaffected.

## Acceptance Criteria

- [ ] edit --title renames the file to the new slug, using git mv when the file is tracked, in the same autocommit as the edit
- [ ] chitty fix renames any task (including archived ones) whose slug no longer matches its title, as a safe repair
- [ ] A rename never overwrites an existing file; it fails loudly instead
- [ ] The MCP edit tool behaves the same as the CLI, because the behaviour lives in store.py
- [ ] Tests with real temp Git repositories cover edit, fix, untracked files and collisions; PLAN.md and README are updated

## Notes

Decided with the human: filenames should broadly reflect titles. This reverses the PLAN.md rule that slugs are never updated. PLAN.md records the decision; update the README with the implementation.

## History

- 2026-10-28 → todo
