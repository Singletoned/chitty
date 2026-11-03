---
title: Refuse ticket writes when the latest version is on another branch
status: todo
priority: high
depends_on:
  - TASK-107
created: 2026-11-02
---

## Description

Reads take each ticket's newest committed version from any branch, but `edit` writes into the current checkout. Editing on `main` a ticket whose latest version is on a work branch forks the ticket file, and the branch merge then conflicts (this happened to `TASK-99` twice). It also moves the latest version to `main`, so `chitty show` stops naming the work branch and reviewers can't find it.

Refuse the write and say where to run it. Decided with the human in `HUMAN-9` (2026-11-03): do not route writes to other branches. With one ticket in work at a time and reviews already run in the ticket's worktree, routing would rarely be used, and no-checkout Git plumbing is the riskiest code Chitty could have. The cost is accepted: a ticket on a branch cannot be edited from `main`.

Out of scope: bulk writes (`archive` with no ID, `fix`), and any automatic routing or merging.

## Acceptance Criteria

- [ ] `edit`, `note`, `move` and `archive <ID>` refuse a ticket whose latest committed version is on another local branch: nothing is written, and the error names the branch and its worktree, or how to check it out if it has none
- [ ] A ticket whose latest version is only on a remote-tracking branch is refused the same way
- [ ] Writes still work when the current checkout holds the latest version, including in the branch's own worktree
- [ ] CLI tests cover the worktree, no-worktree, remote-only and same-branch cases, and an MCP test shows the same error
- [ ] `PLAN.md` and `src/chitty/guide.md` state the rule, and `__version__` is bumped

## Plan

Add one check in the shared store write path, using the existing cross-branch version lookup, so the CLI and MCP cannot diverge. Write the tests first.

## Notes

Blocked pending `HUMAN-1`: the cross-branch write mechanism needs a costly-to-reverse decision on transactional guarantees and whether to split the Git-plumbing work. I traced the current `Repo.edit`/`_save`/`_commit` path and confirmed it writes directly in the caller checkout; a temporary-index implementation must define atomic updates and recovery before coding.

Correction: the required decision is tracked by `HUMAN-9`.

Rewritten after `HUMAN-9`. The old plan and criteria for no-checkout writes are replaced; the earlier blocked notes are history.

## History

- 2026-11-02T13:39:15Z lively-otter → todo
- 2026-11-03T09:42:27Z mellow-marten: wrote the plan
- 2026-11-03T09:42:27Z mellow-marten todo → doing
- 2026-11-03T09:45:07Z mellow-marten: changed dependencies, notes
- 2026-11-03T09:45:07Z mellow-marten doing → blocked
- 2026-11-03T09:45:15Z mellow-marten: changed dependencies, notes
- 2026-11-03T10:40:59Z lively-panda: changed title, dependencies, description, acceptance criteria, notes; wrote the plan
- 2026-11-03T10:40:59Z lively-panda blocked → todo
