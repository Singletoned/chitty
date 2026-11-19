---
title: Test that review-mode `setup` and landing failures are recorded on the ticket branch
status: doing
priority: high
depends_on:
  - TASK-382
parent: TASK-376
created: 2026-11-19
---

## Description

`TASK-382` makes the runner record its errors on the ticket branch instead of `main`. Its branch also carries tests for two review-mode failures that do not yet check what matters: where the error was committed. This ticket strengthens them; it changes tests only. Split from `TASK-382` on 2026-11-19, after reviews found these tests weak (one read `main` before the run instead of after; the landing check failed for a reason other than the reviewer's marker).

All in `tests/test_review_merge.py`, class `TestReviewMerge(ReviewMergeTestCase)`. The fixture is `ReviewMergeTestCase.setUp` plus `branch_for_review()`, which commits work on `task-1` and moves the ticket to `review` there, leaving `main`'s copy at `todo`. The ticket file is `chitty/tasks/TASK-1--review-me.md`; below, `<path>` means that path.

- `test_review_setup_failure_records_error_on_branch`: keep its fixture and action (commit `setup = "false"` to `chitty.toml` on `main`, then `chitty run --mode review`). Before the run, record `git rev-parse main` and `git show main:<path>`. After the run, assert: the output contains `review → error`; `git rev-parse main` is unchanged; `git show main:<path>` equals the copy recorded before the run; `git show task-1:<path>` contains `status: error`, `Runner error (setup)` and `setup exited with status 1`; `git show task-1~1:<path>` contains `status: review` and not `Runner error`.
- `test_landing_failure_records_error_on_branch_without_advancing_main`: its fake reviewer sets the ticket to `done`, writes `review-marker` and commits both, but today it never runs: the test writes it to `self.root / "bin" / "fake"`, while `ReviewMergeTestCase.setUp` puts `self.tmp / "bin" / "fake"` first on `PATH`, so the setUp fake runs instead (it sets `done` but writes no marker; the test passed only because the old check also failed on `done`). Write the test's fake, with its body and `chmod` unchanged, to `self.tmp / "bin" / "fake"`, replacing the setUp one, and drop the `git add bin/fake` and its `configure landing reviewer` commit. Replace its check script body with exactly `from pathlib import Path` and `if Path("review-marker").exists(): raise SystemExit(7)` (no arguments; the check runs in the worktree), dropping the test of the ticket's status. After the run, assert: the output contains `done → error`; `git rev-parse main` is unchanged from before the run; `git show task-1:<path>` contains `status: error`, `Runner error (landing)` and `landing check exited with status 7`; `git show task-1~1:<path>` contains `status: done`; `git diff-tree --no-commit-id --name-only -r task-1` lists only `<path>`.
- Delete the class `TestReviewSetupErrorOnBranch` from `tests/test_run_errors_on_branch.py`: it repeats the first test and reads `main` before the run. Then remove the imports this leaves unused there (`re` and `ReviewMergeTestCase`), or ruff fails.

Evidence. The code exists, so show each test fails against a wrong version of `src/chitty/run.py`, made by hand and not committed: in `_run_ticket`, pass `Repo(main_root, main_repo.config)` instead of `branch_repo` to `_record_ticket_error` (both the review-mode `setup` call and the call in the `except ChittyError` block, which records landing errors). Run the two tests against it, record in a note which assertion fails in each, then restore the file. Both are expected to fail first on `git rev-parse main` being unchanged. To show the landing check fails because of the marker, remove the marker-writing line and its `git add` from the fake: the test then fails on `done → error` (the run ends `review → done`).

No property: two fixed failure phases, both listed and tested; the behaviour drives real Git and runner processes.

## Acceptance Criteria

- [ ] Both tests in `TestReviewMerge` named in the Description pass with every assertion listed there
- [ ] A note records, for each test, the assertion that fails against the wrong version of `run.py` described under Evidence
- [ ] `TestReviewSetupErrorOnBranch` no longer exists; `make check` passes

## History

- 2026-11-19T13:29:50Z quick-ginger-lapwing → backlog
- 2026-11-19T13:34:19Z quick-ginger-lapwing: changed priority, description, acceptance criteria
- 2026-11-19T13:34:19Z quick-ginger-lapwing backlog → planning
- 2026-11-19T13:34:24Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T13:36:37Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T13:36:40Z quick-ginger-lapwing: changed description
- 2026-11-19T13:36:42Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T13:39:22Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T13:39:26Z quick-ginger-lapwing: changed description
- 2026-11-19T13:39:26Z quick-ginger-lapwing planning → todo
- 2026-11-19T14:34:27Z friendly-fawn-urchin todo → doing
