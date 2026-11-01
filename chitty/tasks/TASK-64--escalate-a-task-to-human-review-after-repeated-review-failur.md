---
title: Escalate a task to human review after repeated review failures
status: todo
created: 2026-11-01
---

## Description

TASK-46 bounced between `doing` and `review` three times without converging. Agents reviewing each other's work can loop indefinitely; after a set number of failed reviews the task should go to a human instead.

## Acceptance Criteria

- [ ] The third `review → doing` since the last escalation sets status `blocked` and owner `human` instead, keeping the reviewer's note and adding one that explains the escalation
- [ ] The CLI reports the escalation; MCP returns the blocked task
- [ ] After a human unblocks the task, the count starts again
- [ ] `PLAN.md`, `README.md` and the managed guide describe the rule; `version` is bumped because the guide changes

## History

- 2026-11-01 → todo
