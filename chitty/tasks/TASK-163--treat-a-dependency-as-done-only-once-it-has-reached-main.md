---
title: Treat a dependency as done only once it has reached `main`
status: doing
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

A reviewer commits `done` on the ticket's branch and merges afterwards, and `TASK-131` keeps that order. `Repo.find` reads the newest copy on any branch, so during that window `next_action` in `src/chitty/store.py` sees the dependency as `done`, and lets a dependent `todo` ticket start. `_worktree` then branches it from `main`, which does not yet have the dependency's code. Nothing reports this. It can happen today if a merge fails or a reviewer dies after `done`, and `TASK-162` makes it routine.

In `next_action`, a `todo` ticket waits unless, for each dependency, the file committed on `refs/heads/main` is in its context's archive directory or says `done`. A dependency archived only on an unmerged branch waits too, and one with no file on `main` was never merged, so it waits. Ask `main` directly rather than working out which ref the newest copy came from: `StoredTask.branch` is only a display name, it is `None` for a local copy, and several refs can hold the same file, so a ref check could block a ticket whose `done` is already on `main`. Find the file with `git ls-tree refs/heads/main` over the dependency's `context.directory` and `context.archive_directory`, so `human` tickets work, matching on `ids.parse_filename`, because a title change renames the file. Parse it with `parse`, and let a file that will not parse raise a `ChittyError`, as the history code does. The same ID in both directories is an error, as it is for `find`. The existing error for a reference that cannot be found stays. A squash merge, a deleted branch and `done` committed directly on `main` then all work. Only the local `main` counts, because `_worktree` branches from it, so a remote that is ahead waits for a pull. A branch that is never merged waits for a person, which is right.

With no `refs/heads/main`, or outside a Git repository, keep today's behaviour, because `chitty next` works there. Put the Git read in `src/chitty/git.py`.

Merging before committing `done` was considered and rejected: a failed review must leave `main` untouched, and `TASK-131` relies on the order.

## Acceptance Criteria

- [x] Tests show a dependent `todo` ticket skipped while its dependency is `done` or archived only on an unmerged branch, and selected once `main` says so, including after the branch is deleted and after a title change
- [x] Tests show a repository with no `main` branch keeping today's behaviour, and a dependency in the `human` context working

## Plan

1. Inspect dependency readiness, Git helpers, model/store behavior, and existing tests.
2. Add a Git helper that reads the dependency file from local main, handling missing main/outside Git with today's fallback and surfacing malformed/duplicate records.
3. Gate next_action dependency readiness through that helper while preserving non-Git behavior and human-context support.
4. Add regression tests for unmerged/merged/deleted/title-renamed/archive/no-main cases, run formatting and make check, then record verified criteria and handoff.

## Notes

Second cold read by a fresh Sonnet subagent, 2026-11-04. Replaced my rule: the newest copy's ref cannot answer this, for the reasons now in the description, so it asks `main`. No existing tests should break, because dependency tests run outside Git. Accepted: an archived dependency passes wherever it was archived.

Third cold read by a fresh Sonnet subagent, 2026-11-04, of the redesign. The rule held for every case. Fixed: how to find the file, and an archive on an unmerged branch, which would have let through the bug this ticket fixes, so it now counts only on `main`; this replaces the earlier note's acceptance. Rejected: its query about `TASK-131`'s order, because `done` before merge is what reviewers do today.

## History

- 2026-11-04T20:20:06Z mellow-newt → backlog
- 2026-11-04T20:22:51Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T20:24:24Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T20:24:25Z mellow-newt backlog → todo
- 2026-11-05T18:46:52Z honest-vole todo → doing
- 2026-11-05T18:47:04Z honest-vole: wrote the plan
- 2026-11-05T19:03:03Z honest-vole: ticked acceptance criteria
- 2026-11-05T19:03:03Z honest-vole: ticked acceptance criteria
