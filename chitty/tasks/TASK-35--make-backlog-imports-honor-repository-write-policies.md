---
title: Make backlog imports honor repository write policies
status: review
created: 2026-10-27
---

## Description

Validate imports before writing and make imported task lifecycle and finalization honor archive, formatting, fix, and autocommit configuration.

## Acceptance Criteria

- [x] Import validates all generated task relationships before it writes any file.
- [x] Archived source tasks honor both move and delete archive policies.
- [x] Imports run the same configured fix, formatting, and commit finalization as other writes.

## Plan

Validate every generated task relationship before creating output. Route imports through repository finalization so formatting, safe repairs, and autocommit apply once. Under delete-mode archive policy, omit historical imported tasks and remove their generated relationships from retained tasks; cover validation, lifecycle, and finalization with filesystem-backed tests.

## Summary

Validated generated relationships before writes, preserved move-mode archival, omitted delete-mode historical tasks, and removed retained-task references to omitted IDs. Imported writes now run repository finalization. Verified with make check.

## History

- 2026-10-27 → todo
- 2026-10-27 todo → doing
- 2026-10-27 doing → review
