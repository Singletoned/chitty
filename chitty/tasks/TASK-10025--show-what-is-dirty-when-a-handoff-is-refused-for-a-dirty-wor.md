---
title: Show what is dirty when a handoff is refused for a dirty worktree
status: backlog
created: 2026-11-25
---

## Description

From TASK-C9HGE5 (echonomicon `TASK-213`, folded into `TASK-676` on 2026-11-25 and split out here): a reused worktree held a whitespace-only `chitty.toml` change from an earlier session's formatter, so the worker's move to `review` was refused at handoff for uncommitted changes the worker had not made. Suggestions: show the dirty diff (or at least each path and whether it is staged) in the refusal, and report tracked changes already present when a session starts, so the worker knows they are not its own.

## History

- 2026-11-25T22:35:21Z golden-coral-stoat → backlog
