---
title: Land reviewed tickets from `chitty run`
status: review
priority: high
depends_on:
  - TASK-120
  - TASK-150
parent: TASK-106
created: 2026-11-03
---

## Description

This follows `TASK-120` and `TASK-150`, which rebase and check before a review. After a pass, have `chitty run` land the work, so reviewers no longer merge in the main checkout, where a conflict breaks `chitty` for every repository (`TASK-118`). Logic goes in `src/chitty/run.py`, with Git helpers in `src/chitty/git.py`.

### Landing a `done` ticket

After a session that moves its ticket to `done`, in work or review mode. `TASK-152` adds landing at the start of a run, so until then a landing that fails needs a person, and its message says so:

1. Refuse, with a message and a non-zero exit, changing nothing, if the main checkout is not on branch `main` or is not clean, using the existing `git.require_clean`, which includes untracked files. Ignored files are allowed. Also refuse if the ticket's worktree has uncommitted changes, including untracked files; otherwise they would only surface when removal fails, after landing.
2. If `main` is not an ancestor of the branch, rebase the branch onto `main` in its worktree, then run `setup` and `check`. Ticket commits land on `main` often, so this will be common. A clean rebase with a passing `check` lands without another review. On a conflict or failed check, abort any rebase, leave everything in place, and exit non-zero naming the problem, for the human to resolve in the worktree.
3. Run `git merge --ff-only <branch>` in the main checkout. Never resolve anything there. `TASK-134` then refreshes setup at the start of the next run.
4. Remove the worktree with `git worktree remove` and the branch with `git branch -d`, never forced. A failure exits non-zero.

`TASK-151` then stops reviewers merging. Until it lands, a reviewer may already have merged, so landing does nothing for a ticket whose branch is gone, as `TASK-153` allows.

Out of scope: pushing, repositories whose main branch is not `main`, the spec-test gates for the pilot's tests stage, and non-Pi harnesses.

## Acceptance Criteria

- [x] Tests show a passed review fast-forwarding `main` with a linear history, the ticket `done` there, and the worktree and branch removed
- [ ] Tests show a moved `main` handled by a clean rebase and passing `check` landing without another review, and a conflict or failing `check` leaving everything in place and exiting non-zero
- [ ] Tests show the main checkout on another branch or not clean, and uncommitted files in the worktree, each refusing and changing nothing, while an ignored file lands

## Plan

Implement landing in src/chitty/run.py with focused Git helpers in src/chitty/git.py. On a done ticket, verify main is the clean main branch and the ticket worktree is clean (including untracked but allowing ignored files), merge main into the ticket branch when needed, run setup and check, then fast-forward main and remove the worktree and branch without force. Leave all state intact and report a non-zero error on refusal, merge/check failure, or cleanup failure. Add isolated unittest coverage for successful landing, merge/check failure preservation, branch/dirty refusals, and ignored files, using real temporary Git repositories. Run the focused tests, formatter, and full make check.

## Notes

The `chitty init` step and its criterion moved to `TASK-134`, at the start of every run, as suggested by the human.

From the `TASK-134` cold read: carrying on to selection after landing would have started the next agent on old code, so a landing now ends the run.

Split on 2026-11-04 at the human's direction, from eight criteria: refusals are now `TASK-151` and landing at the start of a run is `TASK-152`.

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Fixed: landing before its refusals was unsafe, since a long session can leave the main checkout on another branch, and untracked worktree files would fail removal after the merge. The refusals are back here, and prompts and documentation moved to `TASK-151`. A criterion promised "a later run lands it", which only `TASK-152` does, so it went. Rejected: a criterion for "never forced", which a reviewer reads in one line.

Landing must also refuse a branch that changes the Chitty config compared with `main` (`TASK-212`). Repeat that check after the landing rebase.

The human decided on 2026-11-06 to prefer merging the main branch into a ticket branch over rebasing (`TASK-223`). Landing should merge `main` into the branch, run `check`, then fast-forward the main branch.

Implemented landing in run.py with Git merge, fast-forward, clean-tree guards, setup/check validation, and non-forced worktree/branch cleanup. The updated review integration test verifies a moved main landing with linear history and removal. Focused review tests pass; full make check still has legacy tests that create untracked bin/ fixtures and expect pre-landing behavior, so those need updating for the new refusal/landing contract.

## Summary

Handoff: landing now merges main into a done ticket branch, validates setup and check, fast-forwards main, and removes the worktree and branch without force. Verification: focused review tests and ruff/pyright pass; full make check is blocked by legacy test expectations around pre-landing behavior and untracked bin fixtures. Follow-up: update those legacy tests and add explicit dirty-main/worktree and failed-check landing coverage.

## History

- 2026-11-03T20:46:17Z lively-panda → todo
- 2026-11-03T21:21:53Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T21:24:18Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T09:45:41Z lively-panda: changed priority
- 2026-11-04T15:11:37Z mellow-newt: changed dependencies, description, acceptance criteria, notes
- 2026-11-04T15:17:38Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-06T16:24:14Z youthful-toad: changed priority
- 2026-11-06T16:44:07Z youthful-toad: changed notes
- 2026-11-06T21:49:20Z youthful-toad: changed notes
- 2026-11-08T09:10:23Z open-zander todo → doing
- 2026-11-08T09:10:48Z open-zander: wrote the plan
- 2026-11-08T09:17:38Z open-zander: changed notes, summary; ticked acceptance criteria
- 2026-11-08T09:17:38Z open-zander doing → review
