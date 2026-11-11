---
title: Ignore recorded conflict resolutions when `chitty run` rebases a review
status: done
labels:
  - bug
priority: high
created: 2026-11-06
---

## Description

On 2026-11-06 `chitty run --mode review` stopped with ``git rebase main` stopped in .../.worktrees/task-144` and exited 1. The human's global Git config sets `rerere.enabled` and `rerere.autoupdate`: Git replayed a recorded resolution for a `chitty.toml` conflict and staged it (`Staged 'chitty.toml' using previous resolution.`), but a rebase still stops after any conflict. `rebase` in `src/chitty/git.py` (from `TASK-120`) then finds no unmerged paths, aborts and raises the `stopped` `ChittyError`, so the review loop dies instead of sending the ticket back.

Decision (cheap to change): run that rebase as `git -c rerere.enabled=false rebase <onto>`. A review must see the branch as it rebases, not with a resolution recorded for another branch, and a conflict goes back to the worker as `Review failed (integration)`, as `TASK-120` designed. Comment the code saying why. Continuing the rebase with the replayed resolution was rejected: nobody would have checked that resolution for this branch.

Tests must not depend on the developer's Git config. Set `rerere.enabled` and `rerere.autoupdate` in the test repository's own config, record a resolution by resolving the same conflict once, and use the existing helpers in `tests/test_review_rebase.py`. No version bump: this changes no guide or `chitty.toml` template. Out of scope: rerere in any other Git command Chitty runs.

## Acceptance Criteria

- [x] A test in `tests/test_review_rebase.py` with `rerere.enabled` and `rerere.autoupdate` set and a recorded resolution for the conflict shows `chitty run --mode review` moving the ticket to `doing` with `Review failed (integration)` naming the file, the rebase aborted and the agent not started; it fails before the fix
- [x] `PLAN.md` says the review rebase ignores recorded resolutions

## Plan

Test first in `tests/test_review_rebase.py`: set `rerere.enabled`/`rerere.autoupdate` in the test repo, record a resolution by resolving the same conflict once and resetting the branch, then expect `Review failed (integration)`. Then run the rebase with `-c rerere.enabled=false` in `git.rebase`, comment why, and add the sentence to step 3 of the review preparation in `PLAN.md`.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-06. It reproduced the stop in a scratch repository and confirmed `-c rerere.enabled=false` leaves the path unmerged. Fixed nothing in the text; adopted its test recipe (record the resolution by resolving the same conflict once, then reset the branch) and the `PLAN.md` place (step 3 of the review preparation). Rejected: isolating global Git config in the test, because the repository's own settings are enough.

Owner set to human only so chitty run leaves this ticket to this session; cleared when done.

Reviewed: inspected the implementation, regression test, and PLAN.md; targeted review-rebase tests (7) and make check (292 Python tests plus Node) pass. Both criteria are satisfied.

## Summary

`git.rebase` now runs `git -c rerere.enabled=false rebase`, with a comment saying why, so a recorded resolution is never replayed into a review and a conflict goes back to the worker as `Review failed (integration)`. `PLAN.md` says so in step 3 of the review preparation.

Verified: `test_a_recorded_resolution_is_not_replayed_into_the_review` sets `rerere.enabled` and `rerere.autoupdate` in the test repository, records a resolution by resolving the conflict once, and failed before the fix with Git's `Staged 'shared.txt' using previous resolution.`; `make check` passes (292 tests plus Node). Until this merges, the human's review loop can export `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=rerere.enabled GIT_CONFIG_VALUE_0=false`.

## History

- 2026-11-06T09:49:33Z youthful-toad → backlog
- 2026-11-06T09:50:30Z youthful-toad: changed notes
- 2026-11-06T09:50:30Z youthful-toad backlog → todo
- 2026-11-06T09:50:31Z youthful-toad: changed owner, notes
- 2026-11-06T09:50:34Z youthful-toad: wrote the plan
- 2026-11-06T09:50:34Z youthful-toad todo → doing
- 2026-11-06T09:55:10Z youthful-toad: changed owner, summary; ticked acceptance criteria
- 2026-11-06T09:55:10Z youthful-toad doing → review
- 2026-11-06T10:04:12Z friendly-newt: changed notes
- 2026-11-06T10:04:12Z friendly-newt review → done
- 2026-11-11T10:18:01Z vivid-yellowhammer: changed parent
