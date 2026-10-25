---
title: Make agent instructions easy to find from --help
status: done
labels:
  - cli
created: 2026-10-25
---

## Description

An LLM agent reading chitty --help should find the agent guide (src/chitty/guide.md, the AGENTS.md block). Today it is only written by chitty init and served as the chitty://guide MCP resource.

## Acceptance Criteria

- [x] chitty guide prints the agent guide, and works outside a chitty repo
- [x] chitty --help points agents at chitty guide
- [x] PLAN.md and README list the command

## Plan

Add a `guide` command to cli.py that prints store.guide() (the same text as the AGENTS.md block and the chitty://guide MCP resource), needing no repo. Add a line to the group docstring so `chitty --help` says agents should run `chitty guide`. Test both in test_cli.py; update PLAN.md's CLI section and the README.
