---
title: Plan which commits on a ticket branch are bookkeeping to squash
status: review
created: 2026-11-16
---

## Description

In the 14 days to 2026-11-16, 2392 of 2870 commits on `main` were `chitty: ...` autocommits. When a ticket lands, collapse its branch's bookkeeping commits into one, keeping implementation commits as they are. The ticket file records its own History, so nothing is lost. Planned 2026-11-22 and split in three: this ticket adds the pure plan; `TASK-574` rewrites the branch with it; `TASK-573` calls that from the landing in `src/chitty/run.py`.

Definitions, for the non-merge commits `main_branch..HEAD` (oldest first, as `git.branch_commits` gives) and a set of ticket directories (each context's directory relative to the repository root):

- A bookkeeping commit has a subject starting `chitty: ` and changes only paths inside the ticket directories (`PurePosixPath.is_relative_to`).
- Every other commit is an implementation commit.

Decisions:

- New pure function `squash_plan(commits: Sequence[BranchCommit], ticket_directories: Sequence[PurePosixPath]) -> SquashPlan | None` in `src/chitty/git.py`, with frozen dataclasses `BranchCommit(sha: str, subject: str, paths: tuple[PurePosixPath, ...])` and `SquashPlan(keep: tuple[str, ...], squashed: tuple[str, ...])` (SHAs, oldest first). It returns `None`, meaning leave the branch as it is, when there are fewer than two bookkeeping commits, or when any implementation commit changes a path inside a ticket directory (reordering would then change what that commit contains), or when any commit changes no path (cherry-picking an empty commit stops). Otherwise `keep` is the implementation commits in order and `squashed` the bookkeeping commits in order.
- A commit that changes no path is neither kind for planning purposes: any such commit makes `squash_plan` return `None`.
- Out of scope: the Git rewrite (`TASK-574`), commits made on `main` directly, and landing (`TASK-573`).

Tests in a new `tests/test_squash_bookkeeping.py`, with Hypothesis (the repository's property tool).

- `squash_plan` property: draw zero to eight commits, each with a subject (drawn text, prefixed `chitty: ` or not) and zero to three paths from `chitty/tasks/<name>.md`, `chitty/human/<name>.md`, `chitty/tasksX/<name>.md` and `src/<name>.py`; ticket directories `chitty/tasks` and `chitty/human`. Expected, computed in the test from the drawn values by the definitions above: `None` in the three stated cases, else `keep` and `squashed` partition the SHAs in order. Fixed example: two `chitty: ` commits of ticket files plus one `chitty: ` commit with no paths gives `None`. Mutant tests with `hypothesis.find`: a version that uses `str.startswith` on paths, one that skips the implementation-commit check, and one that ignores commits with no paths, each produce a mismatch.

## Acceptance Criteria

- [ ] The `squash_plan` property and the fixed example pass, and all three mutant tests find a mismatch
- [ ] `make check` passes

## Plan

Implement pure classification and refusal rules, then verify against an independent property oracle, fixed empty example, and three find-based mutants; run formatting and checks.

## Summary

Implemented the pure squash plan with property, empty-commit and three mutant checks. make check passed.

## History

- 2026-11-16T09:50:21Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:29Z intrepid-coral-raven backlog → planning
- 2026-11-22T10:11:12Z friendly-jade-stoat: changed title, description, acceptance criteria
- 2026-11-22T10:11:12Z friendly-jade-stoat planning → cold-read
- 2026-11-22T10:12:38Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T10:12:38Z friendly-jade-stoat cold-read → planning
- 2026-11-22T10:12:40Z friendly-jade-stoat planning → cold-read
- 2026-11-22T10:14:06Z friendly-jade-stoat: changed title, description, acceptance criteria
- 2026-11-22T10:14:08Z friendly-jade-stoat cold-read → todo
- 2026-11-22T14:34:07Z rosy-jade-badger todo → doing
- 2026-11-22T14:35:59Z rosy-jade-badger: wrote the plan
- 2026-11-22T14:38:10Z rosy-jade-badger: changed summary
- 2026-11-22T14:39:45Z rosy-jade-badger doing → review
