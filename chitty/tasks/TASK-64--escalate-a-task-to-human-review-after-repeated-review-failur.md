---
title: Escalate a task to human review after repeated review failures
status: review
created: 2026-11-01
---

## Description

TASK-46 bounced between `doing` and `review` three times without converging. Agents reviewing each other's work can loop indefinitely; after a set number of failed reviews the task should go to a human instead.

## Acceptance Criteria

- [x] The third `review → doing` since the last escalation sets status `blocked` and owner `human` instead, keeping the reviewer's note and adding one that explains the escalation
- [x] The CLI reports the escalation; MCP returns the blocked task
- [x] After a human unblocks the task, the count starts again
- [x] `PLAN.md`, `README.md` and the managed guide describe the rule; `version` is bumped because the guide changes

## Plan

In `Repo.edit`, count `review → doing` History entries after the last `→ blocked` entry. When this edit would be the third, apply it as `blocked` with owner `human` plus an escalation note. Threshold is a module constant in `store.py`. CLI prints `escalated` instead of `updated`. Regression tests in `TestReviewStatus`, written to fail first; then docs, guide, version bump.

## Notes

MCP gets the escalation through the shared `Repo.edit`; only the CLI path has a test. Re-ran `chitty init` here, which refreshed `AGENTS.md` and `chitty_version`.

## History

- 2026-11-01 → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
