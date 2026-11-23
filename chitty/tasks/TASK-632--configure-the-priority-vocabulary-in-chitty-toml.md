---
title: Configure the priority vocabulary in `chitty.toml`
status: backlog
parent: TASK-607
created: 2026-11-23
---

## Description

Add an optional `priorities` list to `chitty.toml`, ordered highest first; the default is today's `high`, `medium`, `low`, so existing repositories are unchanged. `Frontmatter.priority` (`src/chitty/model.py`, today a `Literal`) is validated against the configured list; `chitty check` reports an unknown value naming the file. `chitty add -p` and `chitty edit -p` (today click choices) and the MCP tools accept the configured values. Document the setting in `docs/plan/config.md`.

## History

- 2026-11-23T10:40:39Z witty-russet-gannet → backlog
