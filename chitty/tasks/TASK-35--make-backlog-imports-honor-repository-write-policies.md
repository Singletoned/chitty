---
title: Make backlog imports honor repository write policies
status: todo
created: 2026-10-27
---

## Description

Validate imports before writing and make imported task lifecycle and finalization honor archive, formatting, fix, and autocommit configuration.

## Acceptance Criteria

- [ ] Import validates all generated task relationships before it writes any file.
- [ ] Archived source tasks honor both move and delete archive policies.
- [ ] Imports run the same configured fix, formatting, and commit finalization as other writes.

## History

- 2026-10-27 → todo
