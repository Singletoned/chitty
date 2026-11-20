---
title: Tell planners to cold-read again when a read found serious problems
status: done
labels:
  - untestable
owner: untestable
created: 2026-11-19
---

## Description

Owner advice 2026-11-19: when a cold read is very useful, another read is often worth it. `src/chitty/roles/plan.md` says to cold-read again after a fix that changes what a worker builds. Make it plain that this applies even when the reader has tried its own suggested fixes, and that a ticket goes to `todo` only after a read that finds nothing serious. Seen with `TASK-418`: its second read found a wrong claim (subclassing a test class reruns its tests), the planner promoted it without a third read, and the third read, run after the work, still found six points a worker had to guess.

## Notes

Reviewed: the human read the changed bullet in `src/chitty/roles/plan.md` on 2026-11-20 and approved it; it matches the Description.

## Summary

Reworded the re-read bullet in `src/chitty/roles/plan.md`: read again after a fix that changes what a worker builds, even when the reader suggested and tried the fix itself; move to `todo` only after a read that finds nothing serious; the split-after-a-third-read rule is kept. No test added (untestable wording; no existing test pins this bullet). `make check` passes (777 tests).

## History

- 2026-11-19T13:22:28Z quick-ginger-lapwing → todo
- 2026-11-19T21:41:04Z daring-amber-kestrel todo → doing
- 2026-11-19T21:42:16Z daring-amber-kestrel: changed summary
- 2026-11-19T21:42:16Z daring-amber-kestrel doing → review
- 2026-11-20T08:25:07Z lively-bronze-crane: changed notes
- 2026-11-20T08:25:07Z lively-bronze-crane review → done
