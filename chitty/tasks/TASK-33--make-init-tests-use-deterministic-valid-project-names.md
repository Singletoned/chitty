---
title: Make init tests use deterministic valid project names
status: done
created: 2026-10-27
---

## Description

TestInit.test_init_rejects_clashing_prefix can fail when tempfile names end in an underscore, which violates the project-name schema before the intended prefix-collision assertion.

## Acceptance Criteria

- [x] TestInit.test_init_rejects_clashing_prefix uses a deterministic valid directory name and make check passes.

## Plan

Reproduce the prefix-collision test setup, isolate it from the random tempfile basename with a fixed valid project directory, then run the focused test and make check.

## Notes

Suggestion origin: chitty

Reviewed: independent review confirmed the test now uses a deterministic valid directory while preserving its assertions.

## Summary

Made the clashing-prefix init test deterministic with a valid fixed directory. Verified with make check (119 tests) and independent review.

## History

- 2026-10-27 → backlog
- 2026-10-27 backlog → todo
- 2026-10-27 todo → doing
- 2026-10-27 doing → review
- 2026-10-27 review → done
