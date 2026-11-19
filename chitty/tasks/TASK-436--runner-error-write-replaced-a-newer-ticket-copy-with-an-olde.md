---
title: Runner error write replaced a newer ticket copy with an older one (TASK-388, 2026-11-19)
status: backlog
created: 2026-11-19
---

## Description

At 16:14:20 on 2026-11-19, `chitty run --mode review` recorded `Runner error (agent): TASK-388 was unchanged` on branch `task-388` (commit `de2c5394`). The parent commit `7302f5dc` had TASK-388 at `status: done`, with a passing `Reviewed:` note and a `Landed by hand` note (added in merge `bd855e4c` at 16:02:37). The new commit has `status: error` and drops both notes. Its body is the older `review` copy from `f7fce425` (main, 16:02:00) plus the new error note, so the runner wrote over the newer copy with an old one. Timeline from the reflogs: 16:02:00, TASK-388 reset from error to review on main. 16:02:24, `reset: moving to HEAD` in the worktree. 16:02:37, merge commit with status done. 16:04:15, main fast-forwarded. 16:10:42, the runner fast-forwarded the branch to main. 16:14:20, the error commit. `_record_ticket_error` (`src/chitty/run.py`) re-reads with `branch_repo.find` but edits with `skip_current_version=True`. Either the worktree file was not what HEAD held, or the review was chosen from the 16:02:00 review copy and that copy was written back. Not explained without session logs (`TASK-276`). Also: the runner began a review of a ticket that main showed as done. Result: `chitty list` showed TASK-388 as error although it had landed.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:07Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:08Z sunny-white-dormouse: changed notes
