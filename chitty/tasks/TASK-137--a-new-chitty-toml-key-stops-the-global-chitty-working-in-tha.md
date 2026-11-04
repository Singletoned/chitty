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

## Notes

Hit again 2026-11-04 on `TASK-136`: `chitty run` picked `review TASK-136`, ran `setup` in the worktree, then failed at `Repo.open(worktree)` with `agent_command: Extra inputs are not permitted`, before any claim or session. The worktree's own `.venv/bin/chitty run` cannot get round it, because `run` reads `agent_command` from the main checkout, which does not have it until the branch lands. Preferred option: warn about an unknown key when the file's `chitty_version` is newer than the running code, and keep refusing otherwise, so a typo still fails loudly. A branch adding a key already has to bump the version. `TASK-150` adds `check`, so it will hit this next.

## History

- 2026-11-04T09:46:24Z lively-panda → backlog
- 2026-11-04T17:03:09Z mellow-newt: changed notes
