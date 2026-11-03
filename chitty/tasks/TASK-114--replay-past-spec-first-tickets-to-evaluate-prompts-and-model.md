---
title: Replay past spec-first tickets to evaluate prompts and models
status: backlog
priority: low
parent: TASK-106
created: 2026-11-03
---

## Description

Small projects never produce enough tickets to measure whether a prompt or model change helped. A spec-first ticket is a ready-made benchmark: rerun its work stage from the base commit in a scratch worktree, with the spec tests as the oracle, and record pass or fail, retries and cost. Use it to test a change before adopting it, and to try removing rules. Needs several finished `spec-first` tickets first. This probably belongs beside Chitty rather than in it.

## History

- 2026-11-03T10:27:50Z lively-panda → backlog
