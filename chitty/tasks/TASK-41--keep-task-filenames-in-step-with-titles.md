---
title: Keep task filenames in step with titles
status: done
created: 2026-10-28
---

## Description

Filenames are <ID>--<slug>.md, but the slug is fixed when the task is created, so after a title edit the filename stops describing the task (e.g. TASK-40). Filenames should broadly reflect titles: rename the file when the title changes, and have chitty fix repair stale slugs in existing tasks. The ID stays the identity, so references are unaffected.

## Acceptance Criteria

- [x] edit --title renames the file to the new slug, using git mv when the file is tracked, in the same autocommit as the edit
- [x] chitty fix renames any task (including archived ones) whose slug no longer matches its title, as a safe repair
- [x] A rename never overwrites an existing file; it fails loudly instead
- [x] The MCP edit tool behaves the same as the CLI, because the behaviour lives in store.py
- [x] Tests with real temp Git repositories cover edit, fix, untracked files and collisions; PLAN.md and README are updated

## Plan

Trace title edits and fix repairs, add failing filesystem and Git rename tests, centralize collision-safe filename reconciliation in store.py for CLI and MCP, update documentation, then run make check.

## Notes

Decided with the human: filenames should broadly reflect titles. This reverses the PLAN.md rule that slugs are never updated. PLAN.md records the decision; update the README with the implementation.

Ready for review: make check passes.

## Summary

Title edits now rename task files safely and fix repairs stale filename slugs. Verified with make check.

## History

- 2026-10-28 → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
- 2026-10-28 review → done
