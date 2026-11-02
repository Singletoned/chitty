---
title: Let a context turn off review, and turn it off for `human`
status: doing
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

1. Extend context configuration to accept an optional `review` override and resolve it over the repository default.
2. Update initialization and upgrade output so the `human` context explicitly disables review, and bump the version because existing repositories must re-run `init`.
3. Add focused configuration and initialization tests, update `PLAN.md` and `README.md`, then run `make check`.

## Notes

Review failed: the current tree has removed the per-context `review` field, resolution logic, generated `human` override, upgrade path, regression tests, and PLAN/README documentation from commit `67eb452`. Restore the implementation and tests for both override directions, then verify `chitty init` upgrades an existing `human` context.

## Summary

Implemented context-level `review` overrides and disabled review in the generated `human` context. Bumped the setup version to `0.1.14`; `chitty init` upgrades existing `human` contexts that lack an explicit setting.

Verified with `make check` (187 tests). Full `chitty check` passed with only pre-existing Markdown warnings in archived tickets.

## History

- 2026-11-01 → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-02 review → doing
