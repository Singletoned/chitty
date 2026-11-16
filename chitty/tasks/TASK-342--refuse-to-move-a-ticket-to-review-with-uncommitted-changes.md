---
title: Refuse to move a ticket to review with uncommitted changes
status: planning
created: 2026-11-16
---

## Description

`src/chitty/roles/work.md` tells workers that `git status --short` must be empty before `-s review`. Enforce it: `chitty edit -s review` in a worktree with uncommitted or untracked non-ignored files refuses and lists them. Then remove the instruction from the guide.

## History

- 2026-11-16T09:59:51Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:32Z intrepid-coral-raven backlog → planning
