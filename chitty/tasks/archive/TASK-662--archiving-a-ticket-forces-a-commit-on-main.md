---
title: Archiving a ticket forces a commit on main
status: backlog
labels:
  - bug
created: 2026-11-24
---

## Description

In shelfpath, `chitty archive 11` run in a `plan/data-bankruptcy` worktree failed with "TASK-11's latest committed version is on branch main; run Chitty in worktree <main checkout>", even though `chitty edit 11` had just committed on that plan branch. The only way through was to fast-forward main and archive from the main checkout, which commits directly on main. The managed AGENTS.md text says "Never commit your changes on main ... branch from it in a worktree as plan/<name>". Archive should work from a plan/ worktree, as edit does. Also: `chitty edit` on a ticket whose latest version is on a ticket branch has no way to cancel that ticket from main; a cancelled status, or an archive that supersedes the branch, would avoid having to delete the ticket branch by hand.

## Notes

Suggestion origin: shelfpath

Archived 2026-11-25: archiving from a plan/ worktree folded into TASK-602, which removes the latest-version-on-another-branch refusal; cancelling from main folded into TASK-599.

Planner, 2026-11-25: covered by TASK-YCGMCS (on a `plan/` branch, `chitty archive <ID>` archives the checkout's copy). Archive this once that lands; it cannot be archived from a plan branch until then.

## History

- 2026-11-24T22:21:25Z zesty-coral-newt → backlog
- 2026-11-24T22:21:26Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:38Z zesty-coral-newt: changed labels
- 2026-11-25T20:46:08Z golden-coral-stoat: changed notes
- 2026-11-25T20:46:15Z golden-coral-stoat backlog → archived
- 2026-11-25T22:59:25Z calm-ochre-quail: changed notes
