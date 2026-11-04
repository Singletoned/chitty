---
title: Stop agents reading the whole of `PLAN.md`
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

From `docs/pi-token-usage.md`, recommendation 6. `PLAN.md` is the most expensive file agents read, at about $3 over the sample, because `AGENTS.md` line 3 tells them to read it before changing behaviour. It is 671 lines in 21 sections. Change that line to say: find the relevant section with `grep -n '^## ' PLAN.md` and read only that, and update it when a decision changes. Keep `PLAN.md` as one file. This line is outside the managed block, so `chitty init` does not touch it, and no version bump is needed.

## Acceptance Criteria

- [ ] `AGENTS.md` says to read only the relevant section of `PLAN.md`, and says how to find it

## History

- 2026-11-04T21:41:07Z mellow-newt → backlog
