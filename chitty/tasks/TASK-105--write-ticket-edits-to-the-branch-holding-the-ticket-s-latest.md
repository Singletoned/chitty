---
title: Write ticket edits to the branch holding the ticket's latest version
status: doing
priority: high
depends_on:
  - TASK-102
created: 2026-11-02
---

## Description

Reads already take each ticket's newest committed version from any branch, but `edit` writes into the current checkout. Editing on `main` a ticket whose latest version is on a work branch forks the ticket file, and the branch merge then conflicts (this happened to `TASK-99` twice). It also moves the latest version to `main`, so `chitty show` stops naming the work branch, and reviewers can't find it.

## Acceptance Criteria

- [ ] `edit` (and other single-ticket writes) on a ticket whose latest version is on another branch writes and commits it on that branch: in that branch's worktree when one is checked out, otherwise without a checkout (e.g. a temporary index and `git commit-tree`)
- [ ] The current checkout is left untouched, and the command reports which branch it wrote to
- [ ] A ticket whose latest version is on a remote-tracking branch only is refused with a clear error, not silently forked
- [ ] Tests cover both the worktree and no-checkout paths and the remote-only refusal; `PLAN.md` documents the rule

## Plan

Trace how Chitty chooses each task version and performs writes, then route writes for a task whose latest version is on another local branch to that branch without changing the caller checkout. Add regression tests for checked-out worktree, no-checkout, and remote-only paths; document the rule in `PLAN.md`, run the full checks, and return the ticket for independent review.

## History

- 2026-11-02T13:39:15Z lively-otter → todo
- 2026-11-03T09:42:27Z mellow-marten: wrote the plan
- 2026-11-03T09:42:27Z mellow-marten todo → doing
