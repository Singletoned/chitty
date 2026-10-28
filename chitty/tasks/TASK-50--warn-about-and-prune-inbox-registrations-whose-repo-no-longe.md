---
title: Warn about and prune inbox registrations whose repo no longer exists
status: backlog
created: 2026-10-28
---

## Description

Registrations in ~/.local/share/chitty/inbox/ can point at directories that no longer exist (deleted temp dirs, scratch clones), so names like 'repo' get taken and suggestions sent there are never pulled. suggest could warn or refuse when the registered path is gone, and there should be a way to list and prune dead registrations. Split from TASK-48.

## Notes

Needs refinement: decide refuse vs warn, and where pruning lives (check/fix are repo-scoped).

## History

- 2026-10-28 → backlog
