---
title: Remove chitty restore and list --archived
status: done
labels:
  - cli
created: 2026-10-26
---

## Description

Archived tasks are looked at by opening the archive folder, and restoring one is manual work (move the file back). Drop the restore command and the list --archived flag to keep the CLI small. list never reads archive folders; --all means every status.

## Acceptance Criteria

- [x] chitty restore and the MCP restore tool are removed
- [x] list --archived is removed; list never includes archived tasks
- [x] --all means every status (archived tasks stay excluded), and the empty-result message no longer mentions archive scope
- [x] Archive folders still count for ID allocation and depends_on resolution
- [x] Shell completion, tests, PLAN.md, README and the agent guide updated

## Plan

Remove restore from CLI/MCP and eliminate list archive-location filtering. Keep storage lookup and allocation behavior unchanged so archived files remain resolvable internally; redefine --all as all statuses among active files only, then update completion tests and docs.

## Notes

Question: Should `chitty archive ID` still accept an already archived ID? Answer: it remains an error as before; restoration is intentionally manual filesystem work.

Verified: restore has no CLI/MCP surface; list reads active folders only and --all selects all active statuses; archived files still resolve and preserve number allocation. Completion/help, docs, make check, and chitty check pass.
