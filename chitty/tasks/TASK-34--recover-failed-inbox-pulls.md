---
title: Recover failed inbox pulls
status: review
created: 2026-10-27
---

## Description

Ensure failed suggestion imports remain recoverable and repository configuration is restored on every exit path.

## Acceptance Criteria

- [x] A failed pull leaves each claimed suggestion available for a later pull.
- [x] Pull always restores the repository configuration after success or failure.
- [x] Regression tests cover failed parsing and failed task creation.

## Plan

Add failure-safe claimed-suggestion handling: restore configuration with a finally block, return unprocessed claims to the waiting state after an exception, and test parse and add failures without filesystem mocks.

## Summary

Restored claimed suggestions on parse and write failures, rolled back tasks created before a note-write failure, and restored repository configuration in finally. Verified with make check.

## History

- 2026-10-27 → todo
- 2026-10-27 todo → doing
- 2026-10-27 doing → review
