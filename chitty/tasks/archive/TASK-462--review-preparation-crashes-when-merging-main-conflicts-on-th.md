---
title: Review preparation crashes when merging main conflicts on the ticket file
status: backlog
created: 2026-11-19
---

## Description

On 2026-11-14 `chitty run --loop --mode review` stopped with exit 1: "TASK-322's latest committed version is on branch main; run Chitty in worktree ...". Cause: `_prepare_review` (`src/chitty/run.py`) merged `main` into `task-322`, which conflicted add/add on `chitty/tasks/TASK-322-...md`. The branch added the file when the ticket was promoted from BACKLOG there; `main` added it separately when `_record_ticket_error` wrote the error note with `skip_current_version=True`. `_fail_review` then edits through the worktree `Repo`, which refuses because main holds the newer version, so the loop dies instead of recording a failure. TASK-319 hit the same add/add conflict. A planner resolved both by hand, taking main's ticket file. Suggest: (1) when the only conflicts are task files under `chitty/`, resolve them to the newest committed version automatically; (2) make `_fail_review` and `_block_dirty_review` write through the repo holding the latest version (as `_record_ticket_error` does) so a review-preparation failure never crashes the loop.

## Notes

Suggestion origin: chitty

Archived as covered by `TASK-370` and the one-authoritative-copy ticket-state model, under which ticket files change only on their branch.

## History

- 2026-11-19T20:55:39Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:40Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:20Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:23Z sunny-white-dormouse backlog → archived
