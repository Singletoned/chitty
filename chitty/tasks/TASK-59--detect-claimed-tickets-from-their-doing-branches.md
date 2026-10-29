---
title: Detect claimed tickets from their doing/ branches
status: backlog
parent: TASK-58
created: 2026-10-29
---

## Description

A ticket is claimed when a `doing/task-<n>--<slug>` branch exists for it. chitty finds such branches with `git for-each-ref` and reads the task file on each with `git show <branch>:<path>`, so listing can show the status and branch of tickets being worked on elsewhere. Open questions: how this surfaces (`chitty list` column, filter, or separate output), whether remote-tracking branches count, and whether a command creates the branch and worktree or the guide just describes the git steps.

## History

- 2026-10-29 → backlog
