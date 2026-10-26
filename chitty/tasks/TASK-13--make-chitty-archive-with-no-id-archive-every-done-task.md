---
title: Make chitty archive with no ID archive every done task
status: todo
labels:
  - cli
created: 2026-10-26
---

## Description

Archiving happens when preparing a merge request, not ticket by ticket. chitty archive with no ID archives every non-archived done task in every context, and reports each one. chitty archive ID still archives a single task.

## Acceptance Criteria

- [ ] chitty archive with no ID archives every non-archived done task across all contexts and lists each archived ID
- [ ] With no done tasks it says so and exits zero
- [ ] chitty archive ID keeps working for a single task
- [ ] MCP archive tool supports the same no-ID form
- [ ] Autocommit makes one commit for the whole batch
- [ ] PLAN.md, README and the agent guide describe archiving at merge-request time
