---
title: Rebase the ticket branch onto `main` before review and landing
status: doing
labels:
  - bug
  - needs-minor
priority: high
depends_on:
  - TASK-382
  - TASK-383
created: 2026-11-18
---

## Description

Principle (decided 2026-11-18, `docs/plan/ticket-state.md`, on branch `plan/ticket-state` until it lands on `main`): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it. Under the one-authoritative-copy model a ticket file changes only on its branch, so ticket files rebase like any other file; there is no ticket merge (`TASK-359` is archived). Any conflict, ticket file or not, goes to an agent.

Today `_prepare_review` merges `main` into the ticket branch with `git.merge_main`, and `_land` merges it again with `git.merge` before fast-forwarding `main` (`src/chitty/run.py`), leaving merge commits on the branch and in `main`.

Decisions:

Starts after `TASK-382` and `TASK-383` land, which stop the runner writing tickets with a branch on `main`; until then a ticket file can change on both sides and conflict.

- New `git.rebase_onto(root: Path, main_branch: str) -> list[str]` in `src/chitty/git.py`: runs `git -c rerere.enabled=false rebase <main_branch>`, without `--autostash` (review and landing already refuse a dirty worktree; `TASK-370` stashes explicitly). Exit 0: return `[]`. Non-zero with a rebase still in progress and unmerged paths (`git diff --name-only --diff-filter=U`): leave it stopped and return those paths. Non-zero with a rebase in progress but no unmerged paths: run `git rebase --abort` and raise `ChittyError` with Git's output. Non-zero with no rebase in progress: raise `ChittyError` with Git's output. `TASK-370` reuses it.
- `_prepare_review` calls it instead of `merge_main`. On conflicts it runs `git rebase --abort` and fails the review as `Review failed (integration): rebasing onto <main> conflicts in <paths>` with each path in backticks, as today's merge failure does. `TASK-375` later replaces the abort with a resolution session.
- `_land` calls it instead of `git.merge`, then fast-forwards `main`. A conflict aborts the rebase and is a landing error, as today.
- Remove `git.merge` and `git.merge_main` once nothing uses them.
- Ctrl-C during either rebase aborts it and raises `RunInterrupted("rebase")` (exit 130): `_prepare_review` adapts its `KeyboardInterrupt` handler, and `_land` gains one. Retarget the two existing tests that patch `chitty.git.merge_main` to raise `KeyboardInterrupt` (`tests/test_review_merge.py` `test_interrupting_the_merge_aborts_it_and_exits_130` and the one in `tests/test_run_lock.py`) to `chitty.git.rebase_onto`, keeping their exit-130 and abort assertions, with `interrupted during rebase`.
- Existing assertions that a review leaves one merge commit (`tests/test_review_merge.py` around lines 287 and 328, `rev-list --merges --count`) now expect `0`.
- The uncommitted-files block before a review stays.
- In `docs/plan/next-action-and-runner.md`, add the principle paragraph, and say under `## Before a review` and `## Landing` that the branch is rebased onto `main`.

Tests: real-Git, fake-agent runner tests in `tests/test_review_merge.py` and `tests/test_landing.py`, with `git init -b main`; the fake reviewer writes a marker file when it starts. No property: real Git and runner processes over the fixed cases in the criteria; `rebase_onto`'s two outcomes are tested directly in `tests/test_git.py`.

## Acceptance Criteria

- [ ] `git.rebase_onto` returns `[]` and leaves no rebase in progress for a clean rebase, and returns the unmerged paths with the rebase stopped for a conflict, in `tests/test_git.py`
- [ ] A review run where `main` has a new commit to a file the branch does not touch: `git rev-list --merges main..task-<n>` is empty, `main` is an ancestor of the branch, and the fake reviewer starts once; this fails before the change
- [ ] A review run whose rebase conflicts on a code file: no rebase is in progress afterwards, the ticket is `doing` with a note containing `Review failed (integration): rebasing onto `main` conflicts in` and the path in backticks, and no reviewer starts; this fails before the change (today's note says `merging`)
- [ ] A landing after a non-conflicting commit on `main` fast-forwards `main` to the rebased branch with no merge commit (`git rev-list --merges` is empty for the landed range); this fails before the change
- [ ] `git.merge` and `git.merge_main` are gone, the retargeted interrupt tests and the flipped merge-count assertions pass, and `docs/plan/next-action-and-runner.md` has the principle and the rebase under both headings; `make check` passes

## Plan

Add direct real-Git tests for rebase_onto clean and conflict outcomes; implement it and remove obsolete merge helpers. Update review preparation and landing to rebase, handling conflicts and Ctrl-C as specified, then update runner tests and runner design docs. Run focused regression tests before and after the fix, format, run make check, and commit implementation changes with a Task: TASK-374 trailer.

## Notes

On hold 2026-11-18: the ticket state model is being redesigned (the ticket branch is authoritative for its ticket while it exists; no runner writes on `main` for in-flight tickets). See `docs/plan/ticket-state.md` on branch `plan/ticket-state`. Re-plan against that before working.

## History

- 2026-11-18T09:51:20Z witty-ginger-falcon → planning
- 2026-11-18T09:52:34Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:56:01Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:56:03Z witty-ginger-falcon: changed description, acceptance criteria
- 2026-11-18T09:56:05Z witty-ginger-falcon planning → todo
- 2026-11-18T15:47:46Z witty-ginger-falcon: changed notes
- 2026-11-18T15:47:46Z witty-ginger-falcon todo → planning
- 2026-11-18T17:57:37Z lively-quartz-crane: changed dependencies, description
- 2026-11-18T17:57:39Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T17:57:41Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T18:00:09Z lively-quartz-crane planning → cold-read
- 2026-11-18T18:02:09Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T18:02:09Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:02:11Z lively-quartz-crane planning → todo
- 2026-11-18T18:17:15Z lively-quartz-crane: changed description
- 2026-11-19T14:20:48Z sunny-bronze-ibis todo → doing
- 2026-11-19T14:21:56Z sunny-bronze-ibis: wrote the plan
