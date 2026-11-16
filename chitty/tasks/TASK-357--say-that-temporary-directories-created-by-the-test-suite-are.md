---
title: Say that temporary directories created by the test suite are allowed
status: backlog
created: 2026-11-16
---

## Description

Seen 2026-11-16 on `TASK-321`: the review guide says to read and change only files inside the worktree, including scratch files. A reviewer took that to forbid the test suite using the system temp dir, set `TMPDIR` inside the worktree, which nested test repositories inside the git worktree and produced 46 failures, then failed the review as `integration`. In `src/chitty/roles/review.md` and `work.md`, make the rule cover files the agent creates, and say that temporary directories the repository tests create for themselves are fine. Revisit when agents run in containers.

## History

- 2026-11-16T10:29:27Z intrepid-coral-raven → backlog
