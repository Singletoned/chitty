---
title: Skip the review check when HEAD has nothing beyond main
status: planning
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
already reads the main checkout's configuration.

Tests, in `tests/test_review_check.py`:

- `prepare()` switches to `task-1` with no commits beyond `main`, so the
  existing tests would start skipping. Add an empty commit on `task-1` at the
  end of `prepare()` (`git commit --allow-empty --quiet -m work`) so they
  still run the check.
- New test, runner workflow (the fixture default, `tests/support.py` line
  15): configure the check as a script that writes a marker file and exits 3,
  stay on `main` (do not call `prepare()`'s switch), set the ticket to
  `doing`, then run `chitty edit 1 -s review`. Assert exit code 0, the ticket
  file says `status: review`, the marker does not exist, and `result.stderr`
  contains `skipped check: HEAD is already on main`.
- New test, merge-only branch: on `task-1`, create a side branch with one
  commit, return to `task-1`, merge it with `--no-ff`, then fast-forward
  nothing else. HEAD is a merge not on `main`. With the failing check script,
  `-s review` fails with `check failed with status 3`.
- New test, tickets workflow: set `workflow = "tickets"` and `review = true`
  in `chitty.toml` (so `-s review` is allowed), same failing script, on
  `main`. The edit fails with `check failed with status 3`.

## Acceptance Criteria

- [ ] In the runner workflow, `-s review` from a checkout whose HEAD has no commits beyond the main branch does not run the check and prints `skipped check`; shown by the new runner test, which fails without the change.
- [ ] With commits beyond the main branch, the check still runs and a failing check still refuses; shown by `test_failure` with the empty commit added to `prepare()`.
- [ ] In the tickets workflow the check still runs on `main`; shown by the new tickets test.
- [ ] `make check` passes.

## History

- 2026-11-22T12:50:12Z friendly-jade-stoat → todo
- 2026-11-22T12:50:24Z friendly-jade-stoat: changed acceptance criteria
- 2026-11-22T12:50:24Z friendly-jade-stoat todo → planning
- 2026-11-22T12:51:35Z friendly-jade-stoat: changed description
