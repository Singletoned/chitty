---
title: Add autocommit and autoformat config options
status: todo
labels:
  - config
created: 2026-10-25
---

## Description

autoformat is the command to run on each file chitty writes, e.g. "mdformat". autocommit already exists as a repo-level bool in chitty.toml; check whether it needs more (e.g. user-level config).

## Acceptance Criteria

- [ ] autoformat config option names the formatter command
- [ ] When autoformat is set, it runs on every written file before the autocommit, so the commit holds the formatted files
- [ ] Order on each write: chitty fix (TASK-10), then autoformat, then autocommit

## Notes

If fix finds a problem it cannot fix, nothing is formatted or committed.
