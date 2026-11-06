---
title: Stop `historical_files` swallowing Git errors
status: done
labels:
  - bug
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

`historical_files` in `src/chitty/git.py` ends its reading of refs with `except ChittyError: return []`. If a branch is deleted between listing refs and reading them, every ticket silently falls back to the current checkout's copy. On `main`, a ticket in `review` on its branch then looks like `todo`, so a worker could select it, reuse its worktree and move it to `doing`. A reviewer deleting its branch while a worker starts makes this possible, and `TASK-162` makes that routine. Any other Git failure there hides the same way.

Let the error surface, so the command fails loudly and a person reruns it. The catch protects one real case: a directory that is not a Git repository, which most tests use. So put `if not is_repository(root): return []` first, and delete the `try`. A repository with no commits needs nothing, because `if not refs` already handles it. To test the failure, wrap `_git` so the branch is deleted just after `for-each-ref`, which is the real race.

## Acceptance Criteria

- [x] A test deleting a branch after refs are listed gets a `ChittyError`, and a test shows a directory that is not a Git repository still returning no history

## Plan

Inspect historical_files and existing Git tests, add regression coverage for a branch disappearing after refs are listed and preserve the non-repository fallback, remove the broad ChittyError catch, then run the focused tests and full make check.

## Notes

Second cold read by a fresh Sonnet subagent, 2026-11-04. It found what the catch protects, so the ticket now says what to do rather than asking the worker to investigate.

Reviewed: historical_files now explicitly returns no history outside Git and surfaces Git errors after ref enumeration; regression tests cover branch deletion and non-repository directories. Focused tests and make check pass.

## Summary

Removed the broad ChittyError fallback from historical_files while preserving an explicit non-repository return. Added regression tests for a branch deleted after refs are listed and for non-Git directories. Verified with focused tests and make check (ruff, pyright, 261 unittest tests, and Node tests).

## History

- 2026-11-04T20:20:07Z mellow-newt → backlog
- 2026-11-04T20:22:53Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T20:22:54Z mellow-newt backlog → todo
- 2026-11-05T19:18:49Z brisk-newt todo → doing
- 2026-11-05T19:18:59Z brisk-newt: wrote the plan
- 2026-11-05T19:27:58Z brisk-newt: ticked acceptance criteria
- 2026-11-05T19:27:58Z brisk-newt: changed summary
- 2026-11-05T19:27:59Z brisk-newt doing → review
- 2026-11-05T19:33:57Z nimble-vole: changed notes
- 2026-11-05T19:33:57Z nimble-vole review → done
- 2026-11-06T16:46:08Z jolly-quail done → archived
