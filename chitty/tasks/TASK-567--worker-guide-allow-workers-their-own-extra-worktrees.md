---
title: "Worker guide: allow workers their own extra worktrees"
status: backlog
created: 2026-11-22
---

## Description

On 2026-11-21 TASK-505 told its worker to check "after the switch" in a detached worktree of `spike/task-378`. The worker returned the ticket to `planning`, citing its instructions. `src/chitty/roles/work.md` (lines 13-17) says to "create your own files, including scratch files, only there [the ticket's worktree]; do not touch the main checkout, other worktrees or files elsewhere on the machine". The worker read that as forbidding a second worktree of its own, which is a fair reading.

The owner's rule (2026-11-21): workers must not change other people's worktrees, but there is no problem with them having two worktrees if they need to.

Suggest rewording that line of the work guide (and the matching review guide line, if any) to say so: a worker may create extra worktrees of its own (for example a detached worktree at another commit, to show a test fails there), must remove them before handing off, and must not change the main checkout or another agent's worktree. Keep the advice general, since the guides reach every repository.

This replaces an earlier version of this suggestion, which wrongly proposed that worker steps must stay inside the ticket's own worktree.

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:36Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:36Z friendly-jade-stoat: changed notes
