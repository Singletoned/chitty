---
title: A new `chitty.toml` key stops the global `chitty` working in that branch's worktree
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

Found 2026-11-04 unblocking `TASK-126`: its branch adds `setup` to `chitty.toml`, so the global `chitty`, running `main`'s code, fails there with `setup: Extra inputs are not permitted`. Anything calling `chitty` by name in that worktree fails until the branch lands, including a worker, a reviewer and possibly the Pi extension, so they must use `.venv/bin/chitty`. Every ticket adding a key hits this; `TASK-136` will with `agent_command`.

Options to weigh: land the schema change on `main` first; warn about unknown keys, and refuse only when `chitty_version` says the file is from a newer version than the code; or have `chitty run` put the worktree's `.venv/bin` first on `PATH`.

## History

- 2026-11-04T09:46:24Z lively-panda → backlog
