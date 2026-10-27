---
title: Remove user-level contexts.toml and cross-repo add -c
status: todo
labels:
  - cli,config
depends_on:
  - TASK-28
parent: TASK-25
created: 2026-10-27
---

## Description

chitty suggest replaces posting into other repos with add -c and ~/.config/chitty/contexts.toml. Remove them to keep the CLI small.

## Acceptance Criteria

- [ ] add -c accepts only contexts in this repo; contexts.toml is no longer read
- [ ] If contexts.toml exists, commands warn once on stderr that it is ignored and to use chitty suggest
- [ ] Tests, PLAN.md, README, add --help and the MCP add description updated
