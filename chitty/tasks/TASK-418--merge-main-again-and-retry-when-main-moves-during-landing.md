---
title: Merge `main` again and retry when `main` moves during landing
status: done
priority: high
created: 2026-11-19
---

## Description

Landing (`_land_locked` in `src/chitty/run.py`) merges `main` into the ticket branch, runs `setup` and the landing check in the worktree, then runs `git merge --ff-only <branch>` in the main checkout (`git.fast_forward`). Other sessions and runners commit to `main` while the check runs, which takes minutes. When `main` gains a commit after the merge, the fast-forward fails (`Diverging branches can't be fast-forwarded`) and the run stops. Seen 2026-11-19 at 11:34 with `TASK-416`: the runner merged `main` at 11:34:29, a planning `chitty edit` committed to `main` at 11:34:43, and landing failed. The landing lock (`locks.landing_lock`) serialises runners, but ordinary Chitty writes on `main` do not take it, and should not wait minutes for a check. Inbox suggestion of 2026-11-14, "Retry landing when main moves during the landing check".

Decisions:

- Make landing an attempt loop of at most `LANDING_ATTEMPTS = 3` attempts (a module-level constant in `src/chitty/run.py`). Each attempt runs the steps from `git.merge(worktree, main_branch)` to `git.fast_forward(main_root, branch)` as today, including the conflict, config and protected-file checks, `setup` and the landing check. When `git.fast_forward` raises `ChittyError` and `git.is_ancestor(main_root, main_branch, branch)` is false (`main` moved), start the next attempt. Any other failure raises as today.
- After the last attempt fails because `main` moved, raise `ChittyError` with the message `main moved during each of the 3 landing attempts` (the number from the constant). `main`, the branch and the worktree are left as they are, so a later run can retry.
- No wait between attempts: each attempt already takes as long as the check.
- Out of scope: a dirty main checkout before landing (`git.require_clean`), which is a separate ticket; making Chitty writes take the landing lock.

Tests: in a new `tests/test_landing_retry.py`. First move `setUp`, `git`, `finish_ticket` and `land` from `TestLanding` in `tests/test_landing.py` into a base class `LandingTestCase(CliTestCase)` there with no test methods; `TestLanding(LandingTestCase)` keeps its tests, and the new `TestLandingRetry(LandingTestCase)` adds only the four below (subclassing `TestLanding` would inherit and rerun all of its tests).

Call `_land` directly with a check command built with `shlex.join([sys.executable, <script>, <main checkout>, <count file>, <mode>])`, a Python script in the test's temporary directory. On each run the script first exits non-zero if the count file already has 10 lines (so an unbounded retry fails instead of hanging), then appends a line to the count file, which lives outside the repository, then acts by mode:

- `once`: on run 1 only, writes a new file named from the run count in the main checkout, then `git -C <main checkout> add` and `commit`.
- `always`: the same on every run.
- `conflict`: on run 1 only, changes the `status:` line of the ticket file in the main checkout from `todo` to `planning`, then adds and commits it.
- `untracked`: on run 1 only, writes `added.txt` in the main checkout without adding it. For this case the test first commits a new `added.txt` on the ticket branch in the worktree.

Check commits by hash: the branch's commits are those in `git rev-list main..<branch>` before landing.

No property: a fixed set of four cases (moves once, moves every time, conflicts on the second merge, fast-forward fails without `main` moving), each listed and tested. Not tested: that the config and protected-file checks rerun on each attempt; a change `main` gains is merged into the branch, so those checks cannot tell a rerun from no rerun.

## Acceptance Criteria

- [x] Mode `once`: `_land` succeeds; `git rev-list main` contains the check's commit and every branch commit; the count file has two lines; the worktree and branch are removed. It fails before the change with the `--ff-only` error
- [x] Mode `always`: `_land` raises `ChittyError` with `main moved during each of the 3 landing attempts`; the count file has three lines; `git rev-list <start>..main` has exactly three commits, none of them a branch commit; the worktree and branch remain
- [x] Mode `conflict`: on the second attempt `_land` raises the existing conflict error, whose message contains `conflicts in`; the count file has one line (the merge fails before the check runs again); no branch commit is in `git rev-list main`; the worktree remains
- [x] Mode `untracked`: `_land` raises `ChittyError` after one attempt: the count file has one line, the message does not contain `main moved`, and `main` and the worktree are unchanged. This passes before the change too; it is the case that rejects retrying on every fast-forward failure. `tests.test_landing` still runs and passes its existing tests. `make check` passes

## Plan

Add a three-attempt loop around the full landing sequence, retrying only when fast-forward fails and main is no longer an ancestor of the ticket branch. Extract the existing landing test setup/helpers into LandingTestCase, then add the four scripted race/failure cases in tests/test_landing_retry.py. Verify the retry test fails before the implementation, run formatting and make check, and commit implementation/tests with a Task: TASK-418 trailer.

## Notes

Review failed (tests): Newly discovered coverage gaps; no earlier review findings. Add the missing assertions before returning for review.
1: fail - `test_retries_when_main_moves_once` asserts that the final `main` tip is in `rev-list main`, which is tautological; it never captures or checks the check script commit hash. Capture that hash when the script commits and assert it is in landed history. The current test passes with the implementation and fails against pre-change `run.py` with the expected `git merge --ff-only` error.
2: pass - `tests.test_landing_retry` passes; against pre-change `run.py`, `test_stops_after_three_main_moves` fails because it gets the ff-only error instead of the three-attempt message.
3: pass - `tests.test_landing_retry` passes; against pre-change `run.py`, `test_conflict_on_retry_stops_before_second_check` fails because it gets the ff-only error instead of `conflicts in`.
4: fail - The untracked test checks the main HEAD and worktree existence, but does not verify that the worktree remains unchanged; snapshot and compare its branch HEAD and tracked and untracked state around landing. The untracked test passes before and after the change as specified. `python -m unittest -v tests.test_landing tests.test_landing_retry` ran 19 tests OK; `make check` passed 721 tests, ruff and pyright.

Review failed (tests): Resolved the two coverage gaps from the prior review. test_retries_when_main_moves_once now captures the check commit hash and asserts that exact hash is in landed history. test_fast_forward_failure_without_main_move_is_not_retried now snapshots the worktree branch HEAD and porcelain status and verifies both remain unchanged. Evidence: .venv/bin/python -m unittest -v tests.test_landing tests.test_landing_retry ran 19 tests OK; make check passed 721 tests, ruff and pyright. Prior review established the retry tests fail against pre-change run.py.

Reviewed: Prior coverage findings are resolved; no new defects found.
1: pass - `make check` ran 722 tests OK; the once test now checks the captured check commit. The earlier review recorded its pre-change ff-only failure.
2: pass - `make check` ran 722 tests OK; the earlier review recorded the pre-change ff-only failure instead of the retry-limit error.
3: pass - `make check` ran 722 tests OK; the earlier review recorded the pre-change ff-only failure instead of the conflict error.
4: pass - `make check` ran 722 tests OK, including existing landing tests; the untracked test now compares worktree HEAD and status. The earlier review recorded that it passes before and after the change.

## Summary

Implemented bounded landing retries and strengthened the reported test gaps. Verification: .venv/bin/python -m unittest -v tests.test_landing tests.test_landing_retry (19 tests) and make check (721 tests, ruff, pyright) pass. Regression evidence: the earlier review confirmed retry tests fail against pre-change run.py. Follow-up commit: 079e812c (Task: TASK-418).

## History

- 2026-11-19T12:06:28Z quick-ginger-lapwing → planning
- 2026-11-19T12:06:46Z quick-ginger-lapwing: changed acceptance criteria
- 2026-11-19T12:06:51Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T12:09:10Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T12:09:13Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T12:09:18Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T12:12:15Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T12:12:18Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T12:12:18Z quick-ginger-lapwing planning → todo
- 2026-11-19T12:13:22Z quick-jade-jay todo → doing
- 2026-11-19T12:14:21Z quick-jade-jay: wrote the plan
- 2026-11-19T12:40:21Z quick-jade-jay: changed summary; ticked acceptance criteria
- 2026-11-19T12:40:21Z quick-jade-jay doing → review
- 2026-11-19T13:29:31Z upbeat-dusky-stoat: changed acceptance criteria, notes
- 2026-11-19T13:29:31Z upbeat-dusky-stoat review → doing
- 2026-11-19T13:43:05Z kind-white-newt: changed notes, summary; ticked acceptance criteria
- 2026-11-19T13:43:05Z kind-white-newt doing → review
- 2026-11-19T13:45:15Z vivid-quartz-eel: changed notes
- 2026-11-19T13:45:15Z vivid-quartz-eel review → done
