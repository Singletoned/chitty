---
title: Run the configured check when `chitty edit` moves a ticket to review
status: cold-read
labels:
  - needs-minor
created: 2026-11-22
---

## Description

Replaces the first half of `TASK-343` (archived 2026-11-22: its branch was 680 commits behind `main` with obsolete partial work). `src/chitty/roles/work.md` tells workers to run checks before `-s review`; `chitty run` already runs the configured check before a review session, so a forgotten check costs a whole session. Make `chitty edit -s review` run the configured check and refuse on failure. The guide change is `TASK-539`.

Rechecked on `main` 2026-11-22: `Repo.edit` in `src/chitty/store.py` has a gate on `entering_review or passing_review`, in a Git checkout (`(self.root / ".git").exists()`) and without `edit.skip_current_version`, which calls `_require_current_version` and then refuses when `git.uncommitted_paths(self.root)` is non-empty. `src/chitty/commands.py` (`TASK-532`) has `run_logged(phase, command, worktree, timeout) -> int`, which writes `.chitty/check.log` (ignored through Git's exclude file), raises `CommandTimedOut`, and lets `FileNotFoundError` and `KeyboardInterrupt` through.

Decisions:

- Inside that gate, only when `entering_review` (not `passing_review`), after the uncommitted-changes refusal passes and only if `self.config.check` is set: print `Running check in <root>...` to stderr and call `commands.run_logged("check", self.config.check, self.root, self.config.command_timeout)`.
  - exit 0: run the uncommitted-changes refusal again (a check that formats or writes files), then `_require_current_version(stored)` again (the check may take minutes), then carry on with the edit.
  - non-zero exit `N`: raise `ChittyError(f"cannot move {task_id} to review; check failed with status {N}; output in `.chitty/check.log`")`.
  - `CommandTimedOut`: raise `ChittyError(f"cannot move {task_id} to review; {error}")`.
  - `FileNotFoundError`: raise `ChittyError(f"cannot move {task_id} to review; check command not found: {command}")`.
  - `KeyboardInterrupt` propagates. In every refusal nothing is written or committed.
- No `check` configured: nothing runs. `skip_current_version` edits (the runner's handoffs) never run it.
- In a work session the runner runs the check before the agent and the agent's `-s review` runs it again; that double cost is accepted.
- `needs-minor`: `chitty edit -s review` now refuses in any repository whose configured check fails.

Tests: new `tests/test_review_check.py`, classes inheriting `ReviewMergeTestCase` from `tests/test_review_merge.py` for its Git helpers. Its `setUp` sets `check`; each test writes its own `check` line into `chitty.toml` and commits it on `main` before branching. Check scripts are Python files run with `sys.executable`, as `tests/test_next.py` does. Cases, on branch `task-1` with `TASK-1` in `doing`:

1. A check that prints `boom` and exits 3: `chitty edit 1 -s review` exits 1 with `check failed with status 3`; `.chitty/check.log` contains `boom`; `TASK-1` stays `doing`; `git log` gains no commit.
2. A check naming a missing command: exits 1 with `check command not found`; `TASK-1` stays `doing`.
3. A check that exits 0 after creating `made.txt`: exits 1 listing `made.txt`; `TASK-1` stays `doing`.
4. Guards that pass before the change too: with `check = "true"`, and with no `check` line, `-s review` moves `TASK-1` to `review`. With a failing check that writes a marker file outside the repository, `Repo.edit` with `Edit(status="review", skip_current_version=True)` moves it to `review`, and `review` to `done` (with a `Reviewed:` note and verdict lines, as `tests/test_review_merge.py` does) succeeds; the marker is never written.

No property: fixed outcomes, each needing a real subprocess and Git repository.

## Acceptance Criteria

- [ ] Cases 1, 2 and 3 in the Description pass, and each fails before the change
- [ ] The guard cases in case 4 pass; `make check` passes

## History

- 2026-11-22T01:11:06Z lively-zinc-newt → cold-read
