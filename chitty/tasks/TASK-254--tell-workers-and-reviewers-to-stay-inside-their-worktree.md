---
title: Tell workers and reviewers to stay inside their worktree
status: doing
created: 2026-11-10
---

## Description

Agents under `chitty run` may now run unrestricted (the `claude` entry uses `bypassPermissions`), so the boundary has to be in the instructions.

Add one line to `src/chitty/roles/work.md` and `src/chitty/roles/review.md`: read and change only files inside this ticket's worktree, including scratch files; do not touch the main checkout, other worktrees or files elsewhere on the machine. Git commands that read other branches, such as `git diff main...`, and `chitty` commands, which read tickets across branches, are fine.

Tests in `tests/test_guide_worktree_boundary.py`, checking the printed guides.

## Acceptance Criteria

- [ ] `chitty guide work <ID>` and `chitty guide review <ID>` both say to read and change only files inside the ticket's worktree, and that reading other branches through Git or `chitty` is fine.

## Plan

Add focused guide tests that assert the work and review guide outputs include the ticket-worktree-only boundary and explicitly allow Git/chitty reads across branches. Add the single boundary instruction to both role guides, run the focused regression test before implementation to confirm failure, then run make format and make check.

## Notes

Possible starting point: `refs/cold-read/TASK-254/1` (`git show refs/cold-read/TASK-254/1:<path>`). Check it against the criteria; don't trust it.

## History

- 2026-11-10T22:10:58Z jolly-heron → backlog
- 2026-11-10T22:13:11Z jolly-heron: replaced notes; changed description, acceptance criteria
- 2026-11-10T22:13:11Z jolly-heron backlog → todo
- 2026-11-10T23:15:51Z calm-raven todo → doing
- 2026-11-10T23:16:10Z calm-raven: wrote the plan
