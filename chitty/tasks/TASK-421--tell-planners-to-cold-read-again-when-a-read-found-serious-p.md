---
title: Tell planners to cold-read again when a read found serious problems
status: todo
labels:
  - untestable
owner: untestable
created: 2026-11-19
---

## Description

Owner advice 2026-11-19: when a cold read is very useful, another read is often worth it. `src/chitty/roles/plan.md` says to cold-read again after a fix that changes what a worker builds. Make it plain that this applies even when the reader has tried its own suggested fixes, and that a ticket goes to `todo` only after a read that finds nothing serious. Seen with `TASK-418`: its second read found a wrong claim (subclassing a test class reruns its tests), the planner promoted it without a third read, and the third read, run after the work, still found six points a worker had to guess.

## History

- 2026-11-19T13:22:28Z quick-ginger-lapwing → todo
