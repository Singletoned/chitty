---
title: Stop `historical_files` swallowing Git errors
status: backlog
labels:
  - bug
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

`historical_files` in `src/chitty/git.py` ends its reading of refs with `except ChittyError: return []`. If a branch is deleted between listing refs and reading them, every ticket silently falls back to the current checkout's copy. On `main`, a ticket in `review` on its branch then looks like `todo`, so a worker could select it, reuse its worktree and move it to `doing`. A reviewer deleting its branch while a worker starts makes this possible, and `TASK-162` makes that routine. Any other Git failure there hides the same way.

Let the error surface, so the command fails loudly and a person reruns it. First find out what the catch was for: if it covers a directory that is not a Git repository, or one with no commits, test for that directly and return `[]` only then. Say what you found in a note.

## Acceptance Criteria

- [ ] A test shows a Git failure while reading refs raising a `ChittyError` rather than returning no history, and the state the catch was protecting still working

## History

- 2026-11-04T20:20:07Z mellow-newt → backlog
