---
title: Let a context turn off review, and turn it off for `human`
status: todo
priority: high
created: 2026-11-01
---

## Description

`review = true` applies to every context, so a person closing their own `human` task gets "setting status done requires -s review first" (2026-11-01, closing HUMAN-5). The workaround, `-s review` then `-s done`, is busywork. Once TASK-57 refuses self-review, it stops working.

## Acceptance Criteria

- [ ] A context can set `review = false` in `[contexts.<name>]`, overriding the repo setting; tests cover both directions
- [ ] `chitty init` writes `review = false` for the `human` context in new and upgraded repos, with a version bump
- [ ] `PLAN.md` and `README.md` describe the setting

## History

- 2026-11-01 → todo
