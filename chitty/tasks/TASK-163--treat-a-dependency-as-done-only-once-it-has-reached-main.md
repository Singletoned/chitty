---
title: Treat a dependency as done only once it has reached `main`
status: backlog
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

A reviewer commits `done` on the ticket's branch and merges afterwards, and `TASK-131` keeps that order. `Repo.find` reads the newest copy on any branch, so during that window `next_action` in `src/chitty/store.py` sees the dependency as `done`, and lets a dependent `todo` ticket start. `_worktree` then branches it from `main`, which does not yet have the dependency's code. Nothing reports this. It can happen today if a merge fails or a reviewer dies after `done`, and `TASK-162` makes it routine.

In `next_action`, a `todo` ticket waits unless each dependency is archived, or the ticket's file as committed on the local `main` branch says `done`. Ask `main` directly rather than working out which ref the newest copy came from: `StoredTask.branch` is only a display name, it is `None` for a local copy, and several refs can hold the same file, so a ref check could block a ticket whose `done` is already on `main`. Find the file on `main` by its ID, because a title change renames it. A squash merge, a deleted branch and `done` committed directly on `main` then all work. Only the local `main` counts, because `_worktree` branches from it, so a remote that is ahead waits for a pull. A branch that is never merged waits for a person, which is right.

With no `refs/heads/main`, or outside a Git repository, keep today's behaviour, because `chitty next` works there. Put the Git read in `src/chitty/git.py`.

Merging before committing `done` was considered and rejected: a failed review must leave `main` untouched, and `TASK-131` relies on the order.

## Acceptance Criteria

- [ ] Tests show a dependent `todo` ticket skipped while its dependency is `done` only on an unmerged branch, and selected once `main` says `done`, including after the branch is deleted, or after a title change, or when its dependency is archived
- [ ] A test shows a repository with no `main` branch keeping today's behaviour

## Notes

Second cold read by a fresh Sonnet subagent, 2026-11-04. Replaced my rule: the newest copy's ref cannot answer this, for the reasons now in the description, so it asks `main`. No existing tests should break, because dependency tests run outside Git. Accepted: an archived dependency passes wherever it was archived.

## History

- 2026-11-04T20:20:06Z mellow-newt → backlog
- 2026-11-04T20:22:51Z mellow-newt: changed description, acceptance criteria, notes
