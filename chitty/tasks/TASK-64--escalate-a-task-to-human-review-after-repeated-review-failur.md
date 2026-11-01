---
title: Escalate a task to human review after repeated review failures
status: doing
created: 2026-11-01
---

## Description

TASK-46 bounced between `doing` and `review` three times without converging. Agents reviewing each other's work can loop indefinitely; after a set number of failed reviews the task should go to a human instead.

## Acceptance Criteria

- [ ] The third `review → doing` since the last escalation sets status `blocked` and owner `human` instead, keeping the reviewer's note and adding one that explains the escalation
- [ ] The CLI reports the escalation; MCP returns the blocked task
- [ ] After a human unblocks the task, the count starts again
- [ ] `PLAN.md`, `README.md` and the managed guide describe the rule; `version` is bumped because the guide changes

## Plan

In `Repo.edit`, count `review → doing` History entries after the last `→ blocked` entry. When this edit would be the third, apply it as `blocked` with owner `human` plus an escalation note. Threshold is a module constant in `store.py`. CLI prints `escalated` instead of `updated`. Regression tests in `TestReviewStatus`, written to fail first; then docs, guide, version bump.

## History

- 2026-11-01 → todo
- 2026-11-01 todo → doing
