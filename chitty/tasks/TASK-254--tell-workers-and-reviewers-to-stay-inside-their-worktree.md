---
title: Tell workers and reviewers to stay inside their worktree
status: backlog
created: 2026-11-10
---

## Description

Agents under `chitty run` may now run unrestricted (the `claude` entry uses `bypassPermissions`), so the boundary has to be in the instructions.

Add one line to `src/chitty/roles/work.md` and `src/chitty/roles/review.md`: read and change only files inside this ticket's worktree, including scratch files; do not touch the main checkout, other worktrees or files elsewhere on the machine. Git commands that read other branches, such as `git diff main...`, are fine.

Tests in `tests/test_guide_worktree_boundary.py`, checking the printed guides.

## Acceptance Criteria

- [ ] `chitty guide work <ID>` and `chitty guide review <ID>` both say to read and change only files inside the ticket's worktree, and that reading other branches through Git is fine.

## History

- 2026-11-10T22:10:58Z jolly-heron → backlog
