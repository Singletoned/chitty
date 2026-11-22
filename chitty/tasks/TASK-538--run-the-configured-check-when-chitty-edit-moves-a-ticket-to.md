---
title: Run the configured check when `chitty edit` moves a ticket to review
status: done
labels:
  - needs-minor
created: 2026-11-22
---

## Description

Replaces the first half of `TASK-343` (archived 2026-11-22: its branch was 680 commits behind `main` with obsolete partial work). `src/chitty/roles/work.md` tells workers to run checks before `-s review`; `chitty run` already runs the configured check before a review session, so a forgotten check costs a whole session. Make `chitty edit -s review` run the configured check and refuse on failure. The guide change is `TASK-539`.

Rechecked on `main` 2026-11-22: `Repo.edit` in `src/chitty/store.py` has a gate on `entering_review or passing_review`, in a Git checkout (`(self.root / ".git").exists()`) and without `edit.skip_current_version`, which calls `_require_current_version` and then refuses when `git.uncommitted_paths(self.root)` is non-empty. `src/chitty/commands.py` (`TASK-532`) has `run_logged(phase, command, worktree, timeout) -> int`, which writes `.chitty/check.log` (ignored through Git's exclude file), raises `CommandTimedOut`, and lets `FileNotFoundError` and `KeyboardInterrupt` through.

Decisions:

- Inside that gate, only when `entering_review` (not `passing_review`), after the uncommitted-changes refusal passes and only if `self.config.check` is set, call `commands.run_logged("check", self.config.check, self.root, self.config.command_timeout)`.
  - exit 0: run the uncommitted-changes refusal again (a check that formats or writes files), then `_require_current_version(stored)` again (the check may take minutes), then carry on with the edit.
  - non-zero exit `N`: raise `ChittyError(f"cannot move {task_id} to review; check failed with status {N}; output in `.chitty/check.log`")`.
  - `CommandTimedOut`: raise `ChittyError(f"cannot move {task_id} to review; {error}")`.
  - `FileNotFoundError`: raise `ChittyError(f"cannot move {task_id} to review; check command not found: {command}")`.
  - `KeyboardInterrupt` propagates. In every refusal nothing is written or committed.
- No `check` configured: nothing runs. `skip_current_version` edits (the runner's handoffs) never run it.
- In a work session the runner runs the check before the agent and the agent's `-s review` runs it again; that double cost is accepted.
- `needs-minor`: `chitty edit -s review` now refuses in any repository whose configured check fails.

Tests: new `tests/test_review_check.py`, classes inheriting `ReviewMergeTestCase` from `tests/test_review_merge.py` for its Git helpers. Its `setUp` already replaces `check = "true"` with a landing-check script that does nothing unless `main-late.txt` or `review-marker` exists; keep that for the existing tests. Each new test replaces that `check` line in `chitty.toml` with its own and commits it on `main` before branching. The check runs in `self.root` of the `Repo` doing the edit (the ticket worktree when run there). Check scripts are Python files run with `sys.executable`, as `tests/test_next.py` does. Cases, on branch `task-1` with `TASK-1` in `doing`:

1. A check that prints `boom` and exits 3: `chitty edit 1 -s review` exits 1 with `check failed with status 3`; `.chitty/check.log` contains `boom`; `TASK-1` stays `doing`; `git log` gains no commit.
2. A check naming a missing command: exits 1 with `check command not found`; `TASK-1` stays `doing`.
3. A check that exits 0 after creating `made.txt`: exits 1 with `the worktree has uncommitted changes: `made.txt``; `TASK-1` stays `doing`.
4. Guard: with a failing check that writes a marker file outside the repository, `Repo.edit` with `Edit(status="review", skip_current_version=True)` moves `TASK-1` to `review`, and the marker is never written.

The existing `tests/test_review_merge.py` tests enter review through `chitty edit` and so now run their landing-check script there; they must still pass unchanged.

No property: fixed outcomes, each needing a real subprocess and Git repository.

## Acceptance Criteria

- [x] Cases 1, 2 and 3 in the Description pass, and each fails before the change
- [x] Guard case 4 passes, every test in `tests/test_review_merge.py` passes unchanged, and `make check` passes

## Plan

Add focused real-Git regression tests for review checks, confirm failures before implementation, then run configured checks within the existing review gate and verify the full suite.

## Notes

Approach recorded; implementation and regression tests have not yet been started or verified.

Before the fix, the three regression cases each failed: edit succeeded instead of refusing.

Reviewed: configured review checks behave as specified; no additional property test warranted for these fixed subprocess outcomes.
1: pass - make check reports 1089 tests OK; running the three new tests with main's store.py loaded reports three failures, each because edit returned 0 instead of 1.
2: pass - make check reports 1089 tests OK, including the skip guard and unchanged tests/test_review_merge.py.

## Summary

Implemented configured review checks and refusal handling. The three regression cases failed before the fix; all four new cases, unchanged review-merge tests, and make check pass. Updated landing-check call counts for the additional check.

## History

- 2026-11-22T01:11:06Z lively-zinc-newt → cold-read
- 2026-11-22T01:13:21Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T01:13:21Z lively-zinc-newt cold-read → todo
- 2026-11-22T02:21:22Z quick-dusky-eel todo → doing
- 2026-11-22T02:23:25Z quick-dusky-eel: wrote the plan
- 2026-11-22T02:23:37Z quick-dusky-eel: changed notes
- 2026-11-22T02:24:22Z quick-dusky-eel: changed notes
- 2026-11-22T02:30:02Z quick-dusky-eel: changed summary
- 2026-11-22T02:30:03Z quick-dusky-eel doing → review
- 2026-11-22T02:34:58Z honest-dusky-urchin: changed notes; ticked acceptance criteria
- 2026-11-22T02:34:58Z honest-dusky-urchin review → done
