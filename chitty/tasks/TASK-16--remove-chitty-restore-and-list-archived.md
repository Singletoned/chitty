---
title: Remove chitty restore and list --archived
status: todo
labels:
  - cli
created: 2026-10-26
---

## Description

Archived tasks are looked at by opening the archive folder, and restoring one is manual work (move the file back). Drop the restore command and the list --archived flag to keep the CLI small. list never reads archive folders; --all means every status.

## Acceptance Criteria

- [ ] chitty restore and the MCP restore tool are removed
- [ ] list --archived is removed; list never includes archived tasks
- [ ] --all means every status (archived tasks stay excluded), and the empty-result message no longer mentions archive scope
- [ ] Archive folders still count for ID allocation and depends_on resolution
- [ ] Shell completion, tests, PLAN.md, README and the agent guide updated
