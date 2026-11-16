---
title: Resolve dependencies the same way show does, across branches
status: planning
created: 2026-11-16
---

## Description

Seen 2026-11-16: `TASK-318` must be edited on its branch (Chitty refuses on `main`: latest committed version is on branch `task-318`), but that branch was 241 commits behind `main` and did not contain `TASK-326`, so `--depends-on TASK-326` was refused as no such task, though `chitty show TASK-326` finds it. Validate dependency IDs with the same lookup `show` uses, which reads every branch.

## History

- 2026-11-16T10:29:26Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:56Z intrepid-coral-raven backlog → planning
