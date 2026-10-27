---
title: Recover failed inbox pulls
status: done
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

## Notes

Review failed: a claimed suggestion can still be lost if one post-finalization inbox-file deletion succeeds and a later deletion fails.

Review failed: KeyboardInterrupt and SystemExit bypass claim recovery after suggestions move to processing.

Reviewed: cleanup now stages sources as .done before deletion, so a deletion failure preserves completed imports and is retried on the next pull. make check passes.

## Summary

Extended claim recovery to BaseException so interrupts cannot strand claimed suggestions. Verified with make check.

## History

- 2026-10-27 → todo
- 2026-10-27 todo → doing
- 2026-10-27 doing → review
- 2026-10-27 review → doing
- 2026-10-27 doing → review
- 2026-10-27 review → doing
- 2026-10-27 doing → review
- 2026-10-27 review → done
