---
title: Run Pi workers and reviewers in their own worktrees
status: review
priority: high
depends_on:
  - TASK-103
created: 2026-11-02
---

## Description

The human wants to run several workers and reviewers at once in one repo without them overwriting each other or the human's own sessions. Today the Pi prompts say nothing about branches, so most agents commit straight to `main`; one built `TASK-98` on a branch that was never merged while another rebuilt it on `main`, and enabling `autocommit` in `chitty.toml` confused a worker sharing the checkout.

Work mode: claim a ticket, create (or reuse, for a ticket already `doing`) a branch and worktree under `.worktrees/` from `main`, do all code and Chitty writes there, and set `review`. Review mode: review the branch in its worktree; on a pass merge it into `main` and remove the branch and worktree; on a fail set `doing` on the branch. Chitty reads task state across branches, so claims must be committed on the branch before work starts so other agents see them.

## Acceptance Criteria

- [x] The Pi work prompt tells workers to do each ticket in a branch and worktree under `.worktrees/`, never in the main checkout, and to resume an existing worktree for a `doing` ticket
- [x] The Pi review prompt tells reviewers to review in the ticket's worktree, merge into `main` on a pass, then remove the branch and worktree
- [x] A worker's claim (`doing`) is committed on its branch before implementation starts, so a second worker does not pick the same ticket; a test or documented check shows it
- [x] Node tests cover the prompt wording; `src/chitty/guide.md` matches it and `__version__` is bumped

## Plan

Add explicit worker and reviewer worktree workflows to the Pi extension prompts and shipped guide. Cover the required wording with Node tests, verify a claim is committed before implementation, bump the package version because `chitty init` distributes the guide, then run the full checks.

## Notes

Depends on `TASK-103`: workers in worktrees break the shared venv until each worktree has its own.

Found while finishing `TASK-99` on a branch: `-s review` set in the worktree is invisible to reviewers, because `chitty list` in `main` reads `main`'s ticket files. I copied the ticket file to `main` by hand (`99b1fcd`). The design must say how ticket state reaches `main`, e.g. Chitty writes ticket edits to the main checkout while code stays on the branch.

Correction to my previous note: reads already merge ticket state from every local and remote branch (`863447a`, `PLAN.md` Principles), so worktree status changes are visible from `main` once committed; the copy in `99b1fcd` was unnecessary. The real gap: a reviewer editing from `main` writes the branch's ticket version into `main`, so ticket files diverge and conflict on merge (as `TASK-99`'s did). The reviewer's pass-and-merge step should handle that, e.g. by merging before the final ticket edit.

Verified `npm test`, `make check`, `chitty check`, and `chitty fix`; the latter retains only pre-existing Markdown-delimiter warnings in older task files. The committed `doing` claim is `1c99a13`, before implementation commit `HEAD~1`.

## History

- 2026-11-02T11:21:00Z lively-otter → todo
- 2026-11-02T11:21:06Z lively-otter: changed dependencies, notes
- 2026-11-02T13:03:36Z lively-otter: changed notes
- 2026-11-02T13:30:16Z lively-otter: changed notes
- 2026-11-03T07:25:54Z mellow-marten: wrote the plan
- 2026-11-03T07:25:54Z mellow-marten todo → doing
- 2026-11-03T07:27:52Z mellow-marten: changed notes; ticked acceptance criteria
- 2026-11-03T07:27:52Z mellow-marten doing → review
