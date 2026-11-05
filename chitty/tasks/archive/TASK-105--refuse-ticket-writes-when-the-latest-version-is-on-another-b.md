---
title: Refuse ticket writes when the latest version is on another branch
status: done
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

- [x] `edit`, `note`, `move` and `archive <ID>` refuse a ticket whose latest committed version is on another local branch: nothing is written, and the error names the branch and its worktree, or how to check it out if it has none
- [x] A ticket whose latest version is only on a remote-tracking branch is refused the same way
- [x] Writes still work when the current checkout holds the latest version, including in the branch's own worktree
- [x] CLI tests cover the worktree, no-worktree, remote-only and same-branch cases, and an MCP test shows the same error
- [x] `PLAN.md` and `src/chitty/guide.md` state the rule, and `__version__` is bumped

## Plan

Write regression tests for CLI and MCP cross-branch refusal cases. Add the shared `Repo` write guard using cross-branch version lookup and actionable worktree/checkout guidance. Update the user-facing rule and version, then run the full check suite and verify each criterion.

## Notes

Blocked pending `HUMAN-1`: the cross-branch write mechanism needs a costly-to-reverse decision on transactional guarantees and whether to split the Git-plumbing work. I traced the current `Repo.edit`/`_save`/`_commit` path and confirmed it writes directly in the caller checkout; a temporary-index implementation must define atomic updates and recovery before coding.

Correction: the required decision is tracked by `HUMAN-9`.

Rewritten after `HUMAN-9`. The old plan and criteria for no-checkout writes are replaced; the earlier blocked notes are history.

Implementation choice: use the existing cross-branch version lookup at the shared store write boundary, rather than front-end-specific checks, so CLI and MCP stay consistent. This is easy to revise and directly follows the ticket decision not to route writes.

Verified all criteria with `make check`: CLI coverage exercises worktree, no-worktree, remote-only and same-branch writes; MCP has the same refusal test; documentation and version are updated.

Ready for independent review. Re-checked all five criteria after `chitty fix`; `make check` passes.

Reviewed: independently verified all five criteria, including cross-branch CLI and MCP coverage; [36mmake check[0m and [36mchitty check[0m pass.

Correction: independent verification ran make check, chitty check, and chitty fix successfully.

## Summary

Implemented a shared store write guard that refuses cross-branch ticket writes with actionable worktree or checkout guidance.

Verification: independently ran make check (212 tests), chitty check and chitty fix; only pre-existing Markdown-delimiter warnings remain.

## History

- 2026-11-02T13:39:15Z lively-otter → todo
- 2026-11-03T09:42:27Z mellow-marten: wrote the plan
- 2026-11-03T09:42:27Z mellow-marten todo → doing
- 2026-11-03T09:45:07Z mellow-marten: changed dependencies, notes
- 2026-11-03T09:45:07Z mellow-marten doing → blocked
- 2026-11-03T09:45:15Z mellow-marten: changed dependencies, notes
- 2026-11-03T10:40:59Z lively-panda: changed title, dependencies, description, acceptance criteria, notes; wrote the plan
- 2026-11-03T10:40:59Z lively-panda blocked → todo
- 2026-11-03T17:39:53Z opal-marten: changed notes; wrote the plan
- 2026-11-03T17:39:53Z opal-marten todo → doing
- 2026-11-03T17:47:32Z opal-marten: changed notes; ticked acceptance criteria
- 2026-11-03T17:49:06Z opal-marten: changed notes
- 2026-11-03T17:49:06Z opal-marten doing → review
- 2026-11-03T18:12:06Z honest-falcon: changed notes, summary
- 2026-11-03T18:12:06Z honest-falcon review → done
- 2026-11-03T18:12:50Z honest-falcon: changed notes, summary
- 2026-11-05T14:44:51Z vivid-wren done → archived
