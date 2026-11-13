---
title: Stop tests registering projects in the real registry
status: backlog
created: 2026-11-12
---

## Description

The real project registry (registered_projects()) on Ed's machine holds test leftovers: chitty-run-txsmwm, chitty-task-123-tlk9qr, prj, probe, repo, t45, task149-scratch, tmp-1soka7lhma, tmp-2dtrbw6oac, tmp-mehm3w3igo, tmp-mn1utr3ave, tmp-us6mtheacd, tmp-xv9qiiwofj, tmp-yhztcyxx4f, tmpoc0f637i. They look like temporary directories from tests or chitty run sandboxes calling register_project. Point the registry (and inbox_path) at a temporary home in tests, and keep chitty run worktrees from registering themselves. A cleanup for entries whose path no longer exists would also help; the 'unknown project' error lists every name, so the junk shows up there.

Found 2026-11-12 while listing projects to post a suggestion.

## Notes

Suggestion origin: /Users/singletoned/src/efficio/margay-eye-south

## History

- 2026-11-12T21:43:35Z kind-yellow-vole → backlog
- 2026-11-12T21:43:37Z kind-yellow-vole: changed notes
