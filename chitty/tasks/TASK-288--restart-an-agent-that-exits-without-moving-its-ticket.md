---
title: Restart an agent that exits without moving its ticket
status: backlog
labels:
  - bug
parent: TASK-275
created: 2026-11-11
---

## Description

- Print-mode Pi has no Chitty extension, so nothing restarts a session that stops early. TASK-270's worker stopped after `make check` failed, leaving uncommitted changes; `chitty run` then raised `TASK-270 was unchanged`, which ended the human's `--loop`.
- The extension restarts the session up to `MAX_CONTINUATIONS` (5) times with `continuationPrompt` (`src/chitty/integrations/pi/chitty.ts`). Move that into `chitty run`: when a work or review agent exits 0 and the ticket status is unchanged, run the agent command again in the same worktree, with the guide followed by that continuation text, up to 5 times. Then raise the existing error.
- This works for any `{prompt}` agent, not just Pi.

## Acceptance Criteria

- [ ] A `chitty run` whose fake agent exits without changing the ticket the first time and moves it to `review` the second time ends with the ticket in `review`, having started the agent twice. It fails today.
- [ ] A fake agent that never changes the ticket is started 6 times in all, then `chitty run` fails with `was unchanged`.

## History

- 2026-11-11T16:17:51Z vivid-yellowhammer → backlog
