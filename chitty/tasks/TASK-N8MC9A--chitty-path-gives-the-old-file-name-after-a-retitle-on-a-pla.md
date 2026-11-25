---
title: "`chitty path` gives the old file name after a retitle on a `plan/` branch"
status: backlog
labels:
  - bug
depends_on:
  - TASK-602
created: 2026-11-25
provisional: true
---

## Description

2026-11-24, in `.worktrees/plan-quick-tickets` (branch `plan/quick-tickets`): `chitty edit TASK-658 --title ...` renamed the file to `chitty/tasks/TASK-658--derive-the-actor-from-antigravity-conversation-id.md`, but `chitty path TASK-658` (and `chitty check "$(chitty path TASK-658)"`) still gave the old `TASK-658--detect-antigravity-sessions-via-antigravity-conversation-id.md`, which no longer exists in that worktree. So `chitty check` failed with "not a task file in any chitty context". It looks like `path` reads the `main` copy instead of this branch's newer copy. `chitty show` in the same worktree gave the right path.

## Notes

Suggestion origin: chitty

Triage 2026-11-25: TASK-602 makes Chitty read tickets from the current branch, which probably fixes this. Recheck once it lands; related to TASK-494.

## History

- 2026-11-25T22:28:41Z calm-ochre-quail → backlog
- 2026-11-25T22:28:43Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:20Z calm-ochre-quail: changed labels, dependencies, notes
