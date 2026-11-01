---
title: Add `chitty next` to say what an agent can work on
status: backlog
depends_on:
  - TASK-70
  - TASK-74
  - TASK-75
created: 2026-11-01
---

## Description

Agents work out what to pick up by reading `chitty list` and applying the guide's rules, which wastes context and goes wrong. Chitty knows the statuses, flags and actors, so it should answer "what can I work on" itself (bookkeeping principle in `PLAN.md`).

Pull order follows Kanban, from the right: finish before starting. Reviews the caller did not work on, then the caller's own `doing` work, then `todo` by priority. Never `backlog`, queued (TASK-70) or blocked (TASK-74) tasks, or another actor's `doing` work.

## Acceptance Criteria

- [ ] `chitty next` prints the best task to pick up and why, and `--all` prints every workable task in pull order
- [ ] Pull order: reviews the caller did not work on, then the caller's `doing` work, then `todo` by priority; `backlog`, queued, blocked and other actors' `doing` tasks are excluded
- [ ] `--json` and an MCP tool return the same answer through shared store code
- [ ] The managed guide tells agents to start with `chitty next` instead of choosing from `chitty list`; `version` is bumped

## History

- 2026-11-01 → backlog
