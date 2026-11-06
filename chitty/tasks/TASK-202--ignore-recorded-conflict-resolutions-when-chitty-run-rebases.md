---
title: Ignore recorded conflict resolutions when `chitty run` rebases a review
status: backlog
labels:
  - bug
priority: high
parent: TASK-106
created: 2026-11-06
---

## Description

On 2026-11-06 `chitty run --mode review` stopped with ``git rebase main` stopped in .../.worktrees/task-144` and exited 1. The human's global Git config sets `rerere.enabled` and `rerere.autoupdate`: Git replayed a recorded resolution for a `chitty.toml` conflict and staged it (`Staged 'chitty.toml' using previous resolution.`), but a rebase still stops after any conflict. `rebase` in `src/chitty/git.py` (from `TASK-120`) then finds no unmerged paths, aborts and raises the `stopped` `ChittyError`, so the review loop dies instead of sending the ticket back.

Decision (cheap to change): run that rebase as `git -c rerere.enabled=false rebase <onto>`. A review must see the branch as it rebases, not with a resolution recorded for another branch, and a conflict goes back to the worker as `Review failed (integration)`, as `TASK-120` designed. Comment the code saying why. Continuing the rebase with the replayed resolution was rejected: nobody would have checked that resolution for this branch.

Tests must not depend on the developer's Git config. Set `rerere.enabled` and `rerere.autoupdate` in the test repository's own config, record a resolution by resolving the same conflict once, and use the existing helpers in `tests/test_review_rebase.py`. No version bump: this changes no guide or `chitty.toml` template. Out of scope: rerere in any other Git command Chitty runs.

## Acceptance Criteria

- [ ] A test in `tests/test_review_rebase.py` with `rerere.enabled` and `rerere.autoupdate` set and a recorded resolution for the conflict shows `chitty run --mode review` moving the ticket to `doing` with `Review failed (integration)` naming the file, the rebase aborted and the agent not started; it fails before the fix
- [ ] `PLAN.md` says the review rebase ignores recorded resolutions

## History

- 2026-11-06T09:49:33Z youthful-toad → backlog
