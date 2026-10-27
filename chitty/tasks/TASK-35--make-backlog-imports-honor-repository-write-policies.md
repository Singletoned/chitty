---
title: Make backlog imports honor repository write policies
status: doing
created: 2026-10-27
---

## Description

Validate imports before writing and make imported task lifecycle and finalization honor archive, formatting, fix, and autocommit configuration.

## Acceptance Criteria

- [x] Import validates all generated task relationships before it writes any file.
- [x] Archived source tasks honor both move and delete archive policies.
- [x] Imports run the same configured fix, formatting, and commit finalization as other writes.

## Plan

Validate every generated task relationship before creating output. Route imports and the agent-guide migration through one repository finalization, rolling back created files and guide changes if finalization fails. Under delete-mode archive policy, omit historical imported tasks and remove their generated relationships from retained tasks; record archive transitions and cover validation, lifecycle, rollback, and finalization with filesystem-backed tests.

## Notes

Review failed: finalization failures leave partial imports, archived imports lack archive history, and the AGENTS.md migration bypasses autocommit.

Review failed: writes before the finalization try block are not rolled back if task or AGENTS.md writes fail.

## Summary

Added rollback for import finalization failures, recorded archived transitions, and included AGENTS.md migration in the import finalization commit. Verified with make check.

## History

- 2026-10-27 → todo
- 2026-10-27 todo → doing
- 2026-10-27 doing → review
- 2026-10-27 review → doing
- 2026-10-27 doing → review
- 2026-10-27 review → doing
