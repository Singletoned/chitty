---
title: Merge `main` into a ticket branch instead of rebasing it
status: doing
priority: high
created: 2026-11-06
---

## Description

The human decided on 2026-11-06 to prefer merging the main branch into a ticket branch over rebasing it. A rebase replays every commit and can hit the same conflict once per commit, as the old setup-upgrade commits on today's branches did. A merge resolves the conflict once and is quicker. A messier history is acceptable. Landing on the main branch stays fast-forward only: the main branch moves to the branch tip, which contains the merge.

Change `_prepare_review` in `src/chitty/run.py`:
- Instead of `git.rebase(worktree, main_branch)`, it calls a new `git.merge_main(worktree, main_branch)`. That runs `git -c rerere.enabled=false merge --no-edit <main_branch>` in the worktree and returns the conflicting paths, or an empty list on success.
- On a conflict it runs `git merge --abort` and fails the review as today, with the note `Review failed (integration): merging `<main_branch>` conflicts in ...`.
- When the branch already contains the main branch, the merge does nothing.
- Replace `rebase_in_progress` with a check for an unfinished merge (`MERGE_HEAD`) in the review path, in the Ctrl-C handling, and in `_worktree`'s "unfinished rebase" refusals. Keep the existing rebase check alongside it in `_worktree`, because a person may still rebase by hand.
- Keep `-c rerere.enabled=false`, for the reason in `git.rebase`'s comment.
- Remove `git.rebase` and `abort_rebase` if nothing else uses them.

Update the tests in `tests/test_review_rebase.py` and `tests/test_run_lock.py` that say "rebase", including the rerere test, which should now record a resolution and check that the merge doesn't replay it. Update README.md and PLAN.md wherever they say a review rebases the branch. `TASK-131` (landing) should merge `main` too; add a note there.

Out of scope: guide text telling agents to rebase, which `TASK-151` rewrites.

## Acceptance Criteria

- [ ] No code path in `src/chitty/run.py` rebases, an unfinished merge in a ticket worktree is refused like an unfinished rebase, `README.md` and `PLAN.md` say "merge", and `make check` passes.
- [ ] Tests show a review of a branch behind the main branch merging it in, so the reviewer sees both changes (a branch with no commits of its own may fast-forward instead); a conflicting branch failing as `integration` with the merge aborted and the worktree clean; a recorded rerere resolution not being replayed; and Ctrl-C during the merge aborting it.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-223/1`; tests failed before and passed after; `make check` OK, 362 tests). Outcomes:
- The config and `AGENTS.md` checks after a merge: confirmed correct, because `main...HEAD` equals `main..HEAD` once `main` is merged in.
- An unfinished merge in a ticket worktree made the review's autocommit fail with `cannot do a partial commit during a merge`: covered by the refusal in criterion 2.
- No merge commit when the branch has no commits of its own: accepted, criterion 1 reworded.
- Ctrl-C during the merge: added to criterion 1, with the message "interrupted during merge".
- Renaming `tests/test_review_rebase.py` to `tests/test_review_merge.py`: accepted.
- The `TASK-131` note: already added.

## History

- 2026-11-06T21:49:17Z youthful-toad → backlog
- 2026-11-06T21:58:26Z youthful-toad: changed acceptance criteria, notes
- 2026-11-06T21:58:26Z youthful-toad backlog → todo
- 2026-11-08T09:19:45Z eager-otter todo → doing
