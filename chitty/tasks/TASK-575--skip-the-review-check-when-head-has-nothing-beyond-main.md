---
title: Skip the review check when HEAD has nothing beyond main
status: doing
created: 2026-11-22
---

## Description

`chitty edit <ID> -s review` runs the configured `check` (here `make check`,
about 3 minutes) before every move into review, with no output meanwhile. The
check exists to gate a worker's ticket branch. When HEAD is already contained
in the main branch, it only re-checks `main`: the human's
`chitty edit TASK-540 -s review --human` from the main checkout spent 3
minutes checking code that had landed in `9027093c`, and looked hung. Under
`chitty run` every branch is checked again by the landing check before it
reaches `main`, so skipping the review check there loses nothing.

Change: in `Repo.edit` (`src/chitty/store.py`, the `if entering_review and
self.config.check:` block, around line 986), skip the check when
`self.config.workflow == "runner"` and
`git.is_ancestor(self.root, "HEAD", self._main_branch())` is true. Use
`is_ancestor`, not `git.branch_commits`: `branch_commits` ignores merge
commits, and a branch whose only new commit is a merge must still be checked.
When skipping, print exactly this line to stderr, with `<main>` replaced by
the value of `self._main_branch()` (for example `main`):

    skipped check: HEAD is already on <main>

The clean-worktree and current-version checks still run. The `tickets`
workflow is unchanged: work there is committed on `main`, so the check stays
its only gate. Linked worktrees need no special case: `_main_branch()`
already reads the main checkout's configuration (not tested here; out of
scope). If the configured main branch does not exist, `git.is_ancestor`
raises its `ChittyError` naming the failed Git command; let it surface, do
not fall back to running or skipping the check.

Tests, in `tests/test_review_check.py`:

- `prepare()` switches to `task-1` with no commits beyond `main`, so the
  existing tests would start skipping. Add an empty commit on `task-1` at the
  end of `prepare()` (`git commit --allow-empty --quiet -m work`) so they
  still run the check.
- Split `prepare()` so its config write and commit can run alone. New test,
  runner workflow (the fixture default, `tests/support.py` line 15): write a
  check script that writes a marker file and exits 3 into `chitty.toml` and
  commit it on `main` as `prepare()` does, without the `task-1` switch; run
  `chitty edit 1 -s doing` (autocommit keeps the tree clean), then
  `chitty edit 1 -s review`. Assert exit code 0, the ticket
  file says `status: review`, the marker does not exist, and `result.stderr`
  contains `skipped check: HEAD is already on main`.
- New test, merge-only branch (a guard: it passes today, and fails for an
  implementation built on `git.branch_commits`): with the failing check
  committed on `main`, create branch `side` from `main` and commit
  `side.txt` on it; create `task-1` from `main`, set the ticket to `doing`
  from `main` first, then `git switch task-1`, `git merge --no-ff side`, and
  make no other commits. `-s review` fails with `check failed with status 3`.
- New test, tickets workflow (a guard: it passes today, and fails for an
  implementation that skips in every workflow): set `workflow = "tickets"` and `review = true`
  in `chitty.toml` (so `-s review` is allowed), same failing script, on
  `main`. The edit fails with `check failed with status 3`.

## Acceptance Criteria

- [ ] In the runner workflow, `-s review` with HEAD already on the main branch does not run the check and prints `skipped check: HEAD is already on main` to stderr; shown by the new runner test, which fails without the change.
- [ ] Regression guard: with a commit beyond the main branch, a failing check still refuses; `test_failure` must still pass after the empty commit is added to `prepare()` (without that commit it would skip).
- [ ] A branch whose only new commit is a merge still runs the check; shown by the new merge-only test.
- [ ] In the tickets workflow the check still runs on `main`; shown by the new tickets test.
- [ ] `make check` passes.

## Notes

Cold read 2: setup wording, guard tests and missing-main behaviour clarified; no change to what is built.

## History

- 2026-11-22T12:50:12Z friendly-jade-stoat → todo
- 2026-11-22T12:50:24Z friendly-jade-stoat: changed acceptance criteria
- 2026-11-22T12:50:24Z friendly-jade-stoat todo → planning
- 2026-11-22T12:51:35Z friendly-jade-stoat: changed description
- 2026-11-22T12:51:51Z friendly-jade-stoat: changed acceptance criteria
- 2026-11-22T12:52:51Z friendly-jade-stoat: changed description, notes
- 2026-11-22T12:52:51Z friendly-jade-stoat planning → todo
- 2026-11-22T15:03:19Z quick-fawn-falcon todo → doing
