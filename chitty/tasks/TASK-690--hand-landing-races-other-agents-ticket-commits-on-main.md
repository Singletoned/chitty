---
title: Hand landing races other agents' ticket commits on main
status: backlog
created: 2026-11-24
---

## Description

Landing a passed review by hand (rebase onto main, make check, ff-only main) failed twice on 2026-11-23 for TASK-624. During the 2-2.5 minute make check, other agents committed chitty: ticket edits to main, so --ff-only was refused. The only changes were under chitty/. A land step (see TASK-340) could rebase again without rerunning the checks when the new main commits touch only ticket files, as the runner presumably needs to as well.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:52Z zesty-coral-newt → backlog
- 2026-11-24T22:21:53Z zesty-coral-newt: changed notes
