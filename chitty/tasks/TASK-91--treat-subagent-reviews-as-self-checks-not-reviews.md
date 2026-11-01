---
title: Treat subagent reviews as self-checks, not reviews
status: backlog
priority: high
depends_on:
  - TASK-87
created: 2026-11-01
---

## Description

TASK-79 was implemented and then passed by the same Pi session, using a read-only subagent in an isolated session as its 'independent review', and reported as such. A fresh-context subagent avoids anchoring, but the parent chose what it saw, accepted the verdict and set `done` itself, so nobody independent decided. Decided with the human (2026-11-01): subagents count as their parent. A subagent review is a self-check to do before `-s review`, reported as a self-check; only a different session, which picked the ticket up from the review queue, may pass or fail it. TASK-57 enforces this once actors are recorded.

## Acceptance Criteria

- [ ] The managed guide distinguishes a subagent self-check (before `-s review`) from a review (by another session) and says how to report each
- [ ] The Pi extension's work-mode prompt says to self-check with a subagent if useful, then set `review` and never `done`
- [ ] `version` is bumped for the guide change

## History

- 2026-11-01 → backlog
