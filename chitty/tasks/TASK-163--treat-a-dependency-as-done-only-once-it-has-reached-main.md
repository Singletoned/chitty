---
title: Treat a dependency as done only once it has reached `main`
status: backlog
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

A reviewer commits `done` on the ticket's branch and merges afterwards, and `TASK-131` keeps that order. `Repo.find` reads the newest copy on any branch, so during that window `next_action` in `src/chitty/store.py` sees the dependency as `done`, and lets a dependent `todo` ticket start. `_worktree` then branches it from `main`, which does not yet have the dependency's code. Nothing reports this. It can happen today if a merge fails or a reviewer dies after `done`, and `TASK-162` makes it routine.

In `next_action`, a `todo` ticket waits unless each dependency is archived, or is `done` and its newest copy's ref has been merged into `main`, checked with `git merge-base --is-ancestor`. In a repository with no `main` branch, keep today's behaviour, because `chitty next` works there. Put the Git check in `src/chitty/git.py`.

Merging before committing `done` was considered and rejected: a failed review must leave `main` untouched, and `TASK-131` relies on the order.

## Acceptance Criteria

- [ ] Tests show a dependent `todo` ticket skipped while its dependency is `done` on an unmerged branch, and selected once that branch is merged or its dependency is archived

## History

- 2026-11-04T20:20:06Z mellow-newt → backlog
