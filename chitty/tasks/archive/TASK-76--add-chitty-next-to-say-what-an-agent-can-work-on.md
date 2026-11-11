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
- [ ] Options narrow the answer by role, for example `--review` (only reviews the caller can do) and `--work` (only implementation: own `doing`, then `todo`)
- [ ] Label filters (for example `--label code-review` or `--label easy`) narrow the answer, so a reviewer or a cheaper model gets only suitable work
- [ ] `chitty next` uses task state from every branch (TASK-84), so work claimed or progressed on another branch is not offered again

## Notes

With the human: callers may have one role (for example only a reviewer), and model level matters (`hard`/`easy` labels). Option names are provisional.

Narrow version split out as `TASK-124` for the pilot. Role options, label filters and caller-aware selection wait for `TASK-110`.

Archived in backlog triage (human approved, 2026-11-11): already done or superseded.

## History

- 2026-11-01 → backlog
- 2026-11-03T12:40:39Z lively-panda: changed notes
- 2026-11-11T10:16:52Z vivid-yellowhammer: changed notes
- 2026-11-11T10:16:53Z vivid-yellowhammer backlog → archived
