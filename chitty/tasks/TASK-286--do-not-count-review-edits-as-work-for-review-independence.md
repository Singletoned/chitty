---
title: Do not count review edits as work for review independence
status: backlog
labels:
  - bug
parent: TASK-283
created: 2026-11-11
---

## Description

- `Task.review_work` in `src/chitty/model.py` counts every `ticked acceptance criteria` event by an actor as work. A reviewer who ticks criteria while the ticket is in `review` is then refused its own verdict transition (seen on TASK-85 in echonomicon).
- Count a tick only if the ticket was not in `review` when it was made, which the History lines before it show. `wrote the plan` and moves to `review` count as now.

## Acceptance Criteria

- [ ] A test: actor A moves a ticket to `review`, actor B ticks a criterion while it is in `review`, then B moves it to `doing` with a failed-review note; the move succeeds. It fails today.
- [ ] A tick made by an actor while the ticket was in `doing` still counts as work, as today.

## History

- 2026-11-11T16:09:09Z vivid-yellowhammer → backlog
