---
title: Keep a failed ticket write from leaving the file changed, and allow dependencies on tickets from `main`
status: review
labels:
  - bug
priority: medium
created: 2026-11-03
---

## Description

Found on 2026-11-03 editing `TASK-126` from its worktree. Adding `depends_on: TASK-129` failed with `no such task`, because that ticket was created on `main` after the branch was cut, although `chitty list` and `chitty next` can see tickets on every branch. The failed `edit` also left the ticket file changed and uncommitted in the worktree, with the error `cannot finalize task write with unresolved problems`. Two questions to settle: whether dependency checks should use the same all-branch view as reads, and whether a refused write should restore the file before exiting. Needs a cold read before work starts.

## Notes

Related, from the `TASK-134` cold read: `_prepare_write` commits whole files, so an automatic upgrade on write sweeps in uncommitted edits to `AGENTS.md` or `chitty.toml`. `TASK-134` only guards `chitty run`.

Checked 2026-11-24 on `main` at `80f6f701`: both halves are fixed. In a linked `task-1` worktree cut before `TASK-2` was added on `main`, `chitty edit TASK-1 --depends-on TASK-2` succeeds with a clean tree, and a failed edit (refusing `pre-commit` hook) leaves `git status --porcelain` empty (`tests/test_failed_writes_restore.py`). The Notes item about `_prepare_write` sweeping uncommitted edits to `AGENTS.md` or `chitty.toml` into its upgrade commit is not fixed (`refresh_setup` refuses on them; `_prepare_write` does not) and not covered by `TASK-464`; it is now `TASK-FER4EB`. Close this one.

## History

- 2026-11-03T21:01:34Z lively-panda → backlog
- 2026-11-03T21:24:19Z lively-panda: changed notes
- 2026-11-24T08:38:00Z kind-navy-toad: changed notes
- 2026-11-24T08:38:18Z kind-navy-toad: replaced notes
- 2026-11-24T08:43:41Z kind-navy-toad: replaced notes
- 2026-11-24T09:07:23Z kind-navy-toad backlog → review
