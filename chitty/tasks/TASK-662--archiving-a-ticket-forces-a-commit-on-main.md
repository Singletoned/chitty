---
title: Archiving a ticket forces a commit on main
status: backlog
created: 2026-11-24
---

## Description

In shelfpath, `chitty archive 11` run in a `plan/data-bankruptcy` worktree failed with "TASK-11's latest committed version is on branch main; run Chitty in worktree <main checkout>", even though `chitty edit 11` had just committed on that plan branch. The only way through was to fast-forward main and archive from the main checkout, which commits directly on main. The managed AGENTS.md text says "Never commit your changes on main ... branch from it in a worktree as plan/<name>". Archive should work from a plan/ worktree, as edit does. Also: `chitty edit` on a ticket whose latest version is on a ticket branch has no way to cancel that ticket from main; a cancelled status, or an archive that supersedes the branch, would avoid having to delete the ticket branch by hand.

## Notes

Suggestion origin: shelfpath

## History

- 2026-11-24T22:21:25Z zesty-coral-newt → backlog
- 2026-11-24T22:21:26Z zesty-coral-newt: changed notes
