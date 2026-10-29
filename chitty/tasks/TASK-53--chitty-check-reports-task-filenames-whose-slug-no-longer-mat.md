---
title: chitty check reports task filenames whose slug no longer matches the title
status: done
created: 2026-10-28
---

## Description

TASK-41 made `chitty fix` rename files whose slug is stale, but `chitty check` exits 0 for them. On 2026-10-28, `check` passed while `fix` then renamed TASK-4, TASK-5, TASK-6 and TASK-40. Every repair `fix` makes should be reportable by `check`, so that a stale filename shows up without anything being written.

## Acceptance Criteria

- [x] `chitty check` reports each task whose filename slug differs from the slug of its title, naming the expected filename, and exits non-zero
- [x] `chitty fix` still repairs it, and `check` passes afterwards
- [x] A regression test fails before the fix and passes after

## Plan

Add a regression test for stale filename slugs, confirm it fails against the current checker, then make `check` validate filename slugs while preserving `fix` repair behaviour. Run the focused test and `make check`, tick criteria, and commit the completed change.

## Notes

Reviewed: `check` derives the expected filename the same way `fix` does, across live and archived tasks. Ran the new tests against the pre-fix `check.py` at 27b961f^: both fail, and both pass with the fix. `make check` passes.

## Summary

Implemented filename-slug validation in `check` while retaining `fix` renames. Added regression coverage for detection and repair, plus the pre-existing duplicate-ID fixture now accounts for its stale slug. Verified with `make check`.

## History

- 2026-10-28 → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
- 2026-10-29 review → done
