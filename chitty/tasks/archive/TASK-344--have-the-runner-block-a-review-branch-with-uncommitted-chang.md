---
title: Have the runner block a review branch with uncommitted changes
status: backlog
created: 2026-11-16
---

## Description

`src/chitty/roles/review.md` tells reviewers to stop, note the paths and block for `human` when the branch has uncommitted changes. The runner can check this before starting a reviewer and block the ticket itself, saving the session. Then remove the rule from the guide.

## Notes

Already done before this ticket was written: `_block_dirty_review` in `src/chitty/run.py` blocks a review whose worktree has uncommitted changes. Removing the matching guide text is part of `TASK-341`. Archived as a duplicate, 2026-11-16.

## History

- 2026-11-16T09:59:54Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:36Z intrepid-coral-raven backlog → planning
- 2026-11-16T10:50:33Z intrepid-coral-raven: changed notes
- 2026-11-16T10:50:33Z intrepid-coral-raven planning → backlog
- 2026-11-16T10:50:34Z intrepid-coral-raven backlog → archived
