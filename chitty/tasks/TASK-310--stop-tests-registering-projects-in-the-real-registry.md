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

The existing leftover registrations (16 inboxes whose repo pointed into temp or scratchpad directories) were deleted by hand on 2026-11-17. Pruning future dead registrations is `TASK-50`.

Triage 2026-11-24, merged from TASK-691: the registry held 41 projects on 2026-11-23, about 10 of them real. `tmps0tf3zag` is registered to `.worktrees/task-401/tmps0tf3zag` in this repository, so some test still registers without a temporary `XDG_DATA_HOME`. Others: `tmp-a3nxft7jox`, `tmp-mh4uvb1knb`, `tmp-vxeisezmeh` (under `/private/var/folders/.../T/tmp.*`), `probe*`, `rep`, `rep2`, `r568`, `t559repo`, `t559show`, `ac`, `ac-probe`, `p520`, `tk`, `duetry` (agent scratchpads). Warning about registrations whose path is gone is TASK-50.

## History

- 2026-11-12T21:43:35Z kind-yellow-vole → backlog
- 2026-11-12T21:43:37Z kind-yellow-vole: changed notes
- 2026-11-17T17:55:08Z kind-umber-toad: changed notes
- 2026-11-24T22:40:04Z zesty-coral-newt: changed notes
