---
title: Require cold reads to challenge acceptance criteria
status: backlog
labels:
  - workflow
  - planning
priority: high
created: 2026-11-13
---

## Description

Cold reads should detect criteria that are vague, bundled, or impossible to verify reliably before implementation begins.

## Acceptance Criteria

- [ ] The cold-read guide requires examining every acceptance criterion individually.
- [ ] The cold-read output identifies vague phrases and bundled behaviours instead of accepting phrases such as `shown by tests` without detail.
- [ ] For each questionable criterion, the cold read states the weakest test setup and observable result that could falsely pass it.
- [ ] The planner must revise or split criteria identified as ambiguous before the ticket enters todo.

## History

- 2026-11-13T19:51:42Z zesty-umber-puffin → backlog
