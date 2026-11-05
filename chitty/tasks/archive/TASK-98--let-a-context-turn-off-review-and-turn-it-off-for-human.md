---
title: Let a context turn off review, and turn it off for `human`
status: done
priority: high
created: 2026-11-01
---

## Description

`review = true` applies to every context, so a person closing their own `human` task gets "setting status done requires -s review first" (2026-11-01, closing HUMAN-5). The workaround, `-s review` then `-s done`, is busywork. Once TASK-57 refuses self-review, it stops working.

## Acceptance Criteria

- [x] A context can set `review = false` in `[contexts.<name>]`, overriding the repo setting; tests cover both directions
- [x] `chitty init` writes `review = false` for the `human` context in new and upgraded repos, with a version bump
- [x] `PLAN.md` and `README.md` describe the setting

## Plan

1. Compare the rejected implementation in `67eb452` with the current configuration and initialization paths, then restore only the per-context review behavior required by this ticket.
2. Restore focused tests for both override directions and the existing-repository `human` upgrade path; update generated configuration and documentation.
3. Run formatting and `make check`, inspect the diff, tick the criteria, and prepare the ticket for independent review.

## Notes

Review failed: the current tree has removed the per-context `review` field, resolution logic, generated `human` override, upgrade path, regression tests, and PLAN/README documentation from commit `67eb452`. Restore the implementation and tests for both override directions, then verify `chitty init` upgrades an existing `human` context.

Reviewed: independent implementation committed by Ed Singleton verified. Confirmed per-context override resolution in both directions, generated and upgraded human review override, managed-setup version bump, and PLAN.md/README.md documentation. make check passes (188 tests, ruff, pyright).

## Summary

Restored per-context `review` overrides and generated `human.review = false`; `chitty init` now upgrades existing human contexts without changing explicit values. Bumped the managed-setup version to `0.1.15`.

Verification: restored regression tests failed before the implementation; `make format` and `make check` pass afterward.

## History

- 2026-11-01 → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-02 review → doing
- 2026-11-02 doing → review
- 2026-11-02T09:18:34Z pi-reviewer review → done
- 2026-11-05T14:44:50Z vivid-wren done → archived
