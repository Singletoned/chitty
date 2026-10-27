---
title: Remove user-level contexts.toml and cross-repo add -c
status: done
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

- [x] add -c accepts only contexts in this repo; contexts.toml is no longer read
- [x] If contexts.toml exists, commands warn once on stderr that it is ignored and to use chitty suggest
- [x] Tests, PLAN.md, README, add --help and the MCP add description updated

## Plan

Remove user contexts from add target resolution, retain a clear ignored-file warning, and update CLI/MCP/docs/tests so cross-project work uses suggest.

## Notes

Removed user-context resolution and cross-repository add behavior; a legacy contexts.toml now causes a clear suggest migration warning. Updated CLI/MCP descriptions, docs, and regression coverage. Full make check passes.
