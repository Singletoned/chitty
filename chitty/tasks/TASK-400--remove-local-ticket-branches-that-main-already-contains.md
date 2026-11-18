---
title: Remove local ticket branches that `main` already contains
status: cold-read
depends_on:
  - TASK-396
parent: TASK-376
created: 2026-11-18
---

## Description

Under the one-authoritative-copy model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket branch whose tip `main` contains is merged or stale, and reads ignore it (`TASK-377` rule 2). The owner decided on 2026-11-18 that such branches should go: if a branch equals `main`, or is behind it (which a rebase would turn into equal), delete it. Reads never do this; the runner does, as a clean-up step. Several such `task-*` branches exist today.

Starts after `TASK-396` (`git.is_ancestor`) lands.

Decisions:

- At the start of every `chitty run` (before `_land_pending` and selection), the runner removes each local ticket branch (as `TASK-378` defines ticket branches) whose tip `main` contains, using `git.is_ancestor(root, <branch tip>, <main tip>)`: first its linked worktree, if any, then the branch (`git.remove_worktree`, `git.delete_branch`). It prints `removed merged branch <b>` to stderr for each.
- It leaves a branch alone, printing `kept merged branch <b>: <reason>`, when its worktree has uncommitted or untracked files, or a merge or rebase in progress, or is the main checkout.
- Remote-tracking branches are never deleted: they are not this machine's.
- A branch with commits `main` lacks is left alone, whatever its ticket says.
- Update `docs/plan/next-action-and-runner.md` with the clean-up step.

Tests: real-Git runner tests in a new `tests/test_run_removes_merged_branches.py`, in the style of `tests/test_landing.py` (configured `setup` and `check`, fake agent), with `git init -b main`. No property: a fixed set of branch states, each in the criteria.

## Acceptance Criteria

- [ ] `chitty run` removes a local `task-<n>` equal to `main` and one behind `main`, with their clean worktrees, and prints `removed merged branch` for each; this fails before the change
- [ ] It keeps, with a `kept merged branch` line, a merged branch whose worktree has an uncommitted file, and one whose worktree has a rebase in progress; it never removes a branch ahead of `main`, a non-ticket branch such as `feature`, or a remote-tracking `origin/task-<n>`
- [ ] `docs/plan/next-action-and-runner.md` describes the clean-up step; `make check` passes

## History

- 2026-11-18T18:00:02Z lively-quartz-crane → backlog
- 2026-11-18T18:00:04Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T18:00:04Z lively-quartz-crane backlog → cold-read
