---
title: Do not count review edits as work for review independence
status: doing
labels:
  - bug
parent: TASK-283
created: 2026-11-11
---

## Description

- `Task.review_work` in `src/chitty/model.py` counts every `ticked acceptance criteria` event by an actor as work. A reviewer who ticks criteria while the ticket is in `review` is then refused its own verdict transition (seen on TASK-85 in echonomicon).
- Count a tick only if the ticket was not in `review` when it was made, which the History lines before it show. Use line order, not timestamps: one edit writes its event line before its transition line, in the same second, so a tick counts as made in the status its edit started from. A tick in the edit that moves `review` → `doing` or `done` is not counted. `wrote the plan` and moves to `review` count as now.

## Acceptance Criteria

- [ ] A test: actor A moves a ticket to `review`, actor B ticks a criterion while it is in `review`, then B moves it to `doing` with a failed-review note; the move succeeds. It fails today.
- [ ] A tick made by an actor while the ticket was in `doing` still counts as work, as today.
- [ ] A `wrote the plan` by the reviewer while the ticket is in `review` still blocks that reviewer's verdict, as today.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-286/1`. Check it against the current criteria; do not trust it.

## History

- 2026-11-11T16:09:09Z vivid-yellowhammer → backlog
- 2026-11-11T16:09:47Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T16:13:30Z vivid-yellowhammer: changed description
- 2026-11-11T16:13:31Z vivid-yellowhammer: changed acceptance criteria, notes
- 2026-11-11T16:13:31Z vivid-yellowhammer cold-read → todo
- 2026-11-11T21:09:26Z witty-dusky-toad todo → doing
