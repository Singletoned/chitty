---
title: Check saved worktree work round-trips with a property
status: done
depends_on:
  - TASK-534
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-524` on 2026-11-21. After `TASK-524` and `TASK-534`, `git.save_work` and `git.restore_work` save and restore uncommitted work under `refs/chitty/stash/<ID>`. This ticket adds a generated round-trip property. Both landed on `main` 2026-11-22, with example tests in `SavedWorkTests` in `tests/test_git_saved_work.py`; add the property to that file as a separate `unittest.TestCase` class.

Property `test_save_then_restore_round_trips` in `tests/test_git_saved_work.py`, Hypothesis with `@settings(max_examples=25, deadline=None)`, as in `tests/test_git.py`: draw 1 to 6 files committed on `main`, and, independently for each, one change: unchanged, edited and left unstaged, edited and staged, edited, staged and edited again, or deleted; then 0 to 3 new untracked files and 0 to 2 ignored files (listed in a committed `.gitignore`), with random printable contents. An example whose only change is to ignored files is redrawn with `assume`. Names come from fixed pools: tracked `f0.txt` to `f5.txt`, untracked `n0.txt` to `n2.txt`, ignored `i0.log` and `i1.log` (`.gitignore` holds `*.log`), plus a tracked `base.txt` outside the pools. First, on the clean tree, edit `base.txt` and `git stash push` it; record `git stash list`. Then make the drawn changes and record the bytes (or absence) of every name in the tracked and untracked pools and every ignored file's bytes. After `save_work(root, "refs/chitty/stash/TASK-1", "m")`: `True`, `git status --porcelain` empty, the ref exists, ignored files unchanged. Then, at random, commit a new `main-only.txt` (never a drawn name). After `restore_work`: `True`, every recorded file has its recorded bytes or absence, ignored files unchanged, the ref gone, and `git stash list` equals the recorded list.

Suggested structure (from a cold reader whose probe of this property passed at 300 examples on `main` 2026-11-22): module constants `REF`, `TRACKED_POOL`, `UNTRACKED_POOL`, `IGNORED_POOL`, `BASE_NAME`; `git(root, *args)` as in `SavedWorkTests.git`; `make_repo(root)` committing the drawn tracked files, `base.txt` and `.gitignore`; `apply_change(root, name, change, content)` with `change` one of `keep`, `unstaged`, `staged`, `restaged`, `delete`; `snapshot(root, names) -> dict[str, bytes | None]`; an `@st.composite` `scenario()`; and the test method following the steps above.

## Acceptance Criteria

- [x] The round-trip property passes, and fails (with any assertion or error) against a `restore_work` that skips `git update-ref -d` and against a `save_work` that omits `git add -A`; a note records each run and its actual failure; `make check` passes

## Plan

Add a generated isolated Git repository round-trip test, verify both specified mutations fail, then run formatting and checks.

## Notes

Mutation runs: removing `update-ref -d` failed with `assertNotIn` because the saved ref remained; omitting `git add -A` failed with `ChittyError: git stash create produced no commit` for an untracked-only example. Both mutations were reverted.

Reviewed: Property and complete diff inspected; no additional defects found.
1: pass - `make check` printed 1079 tests OK; the worker's mutation runs recorded `assertNotIn` for the retained ref and `ChittyError: git stash create produced no commit` without `git add -A`.

## Summary

Added generated saved-work round-trip coverage. Both requested mutations failed as recorded; make check passed.

## History

- 2026-11-22T00:06:31Z lively-zinc-newt → planning
- 2026-11-22T01:29:59Z lively-zinc-newt: changed description
- 2026-11-22T01:29:59Z lively-zinc-newt planning → cold-read
- 2026-11-22T01:34:09Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T01:34:09Z lively-zinc-newt cold-read → todo
- 2026-11-22T02:01:50Z brisk-ebony-marten todo → doing
- 2026-11-22T02:03:38Z brisk-ebony-marten: wrote the plan
- 2026-11-22T02:04:45Z brisk-ebony-marten: changed notes
- 2026-11-22T02:06:19Z brisk-ebony-marten: changed summary
- 2026-11-22T02:06:21Z brisk-ebony-marten doing → review
- 2026-11-22T02:11:45Z zesty-amber-falcon: changed notes; ticked acceptance criteria
- 2026-11-22T02:11:45Z zesty-amber-falcon review → done
