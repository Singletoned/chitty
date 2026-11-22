---
title: Skip the review check when HEAD has nothing beyond main
status: planning
created: 2026-11-22
---

## Description

`chitty edit <ID> -s review` runs the configured `check` (here `make check`,
about 3 minutes) before every move into review, with no output meanwhile. The
check exists to gate a worker's ticket branch. When the checkout has no
commits that are not already on the main branch, it only re-checks `main`:
the human's `chitty edit TASK-540 -s review --human` from the main checkout
spent 3 minutes checking code that had landed in `9027093c`, and looked hung.
Under `chitty run` every branch is checked again by the landing check before
it reaches `main`, so skipping the review check there loses nothing.

Change: in `Repo.edit` (`src/chitty/store.py`, the `if entering_review and
self.config.check:` block, around line 986), run the check only when
`self.config.workflow == "runner"` is false, or when
`git.branch_commits(self.root, self._main_branch())` is non-empty. Otherwise
skip it and print one line to stderr:
`skipped check: HEAD has no commits beyond <main>` (with the branch name).
The clean-worktree and current-version checks still run. The `tickets`
workflow is unchanged: work there is committed on `main`, so the check stays
its only gate.

Tests, in `tests/test_review_check.py`:

- `prepare()` switches to `task-1` with no commits beyond `main`, so the
  existing tests would start skipping. Add an empty commit on `task-1` in
  `prepare()` (`git commit --allow-empty -m work`) so they still exercise the
  check.
- New test: runner workflow (the fixture's default; confirm), check is a
  script that writes a marker file and exits 3, the main checkout on `main`
  with no extra commits. `chitty edit 1 -s review` from `main` succeeds, the
  ticket is in `review`, the marker does not exist, and stderr contains
  `skipped check`.
- New test: same script, `workflow = "tickets"` in `chitty.toml`, on `main`.
  The edit fails with `check failed with status 3`.

## Acceptance Criteria

- [ ] In the runner workflow, `-s review` from a checkout whose HEAD has no commits beyond the main branch does not run the check and prints `skipped check`; shown by the new runner test, which fails without the change.
- [ ] With commits beyond the main branch, the check still runs and a failing check still refuses; shown by `test_failure` with the empty commit added to `prepare()`.
- [ ] In the tickets workflow the check still runs on `main`; shown by the new tickets test.
- [ ] `make check` passes.

## History

- 2026-11-22T12:50:12Z friendly-jade-stoat → todo
- 2026-11-22T12:50:24Z friendly-jade-stoat: changed acceptance criteria
- 2026-11-22T12:50:24Z friendly-jade-stoat todo → planning
