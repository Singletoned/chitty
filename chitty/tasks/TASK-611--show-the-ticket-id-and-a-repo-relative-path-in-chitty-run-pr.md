---
title: Show the ticket ID and a repo-relative path in `chitty run` progress lines
status: done
created: 2026-11-23
---

## Description

`chitty run` prints `Running check in <absolute worktree path>...` (`_run_check`, `src/chitty/run.py:1463`). In a narrow terminal the useful part, the ticket worktree name, is cut off, and the line does not say which ticket it is for. Seen in taidy, 2026-11-22: `Running check in /Users/.../taidy/.worktrees/task-4...`. The `log: <path>` line printed at the end of a run (`run.py:475`) has the same problem.

Change:

- Add a pure function `display_path(path: Path, main_root: Path) -> str` to `run.py`: the path relative to `main_root` when it is inside it, otherwise `str(path)` unchanged. Use `path.is_relative_to(main_root)`, and `relative_to` only inside it (no try/except). Compare the paths as given, without resolving symlinks or `..`; the main root and Git common dir are resolved (`git.main_checkout`, `git_common_dir`); worktree paths come from `main_root / ".worktrees"` or from `git worktree list`, which prints real paths. Criterion 2 checks the printed form end to end. `path == main_root` gives `.`. A log under a Git directory outside the main checkout (separate git dir) is printed absolute; that fallback is intended. For the check line, pass `main_root` (already in scope in `_run_ticket_with_log`, about `run.py:488`) into `_run_check` as a new parameter right after `branch_repo` (its only caller is `run.py:613`). For the `log:` line, use `main_repo.root` (in scope in `_run_ticket`, `run.py:475`). In `tests/test_next.py:1335`, match `running check in`.
- The check line becomes `<ID>: running check in <display_path(worktree)>...`, for example `TASK-4: running check in .worktrees/task-4...`.
- The log line becomes `log: <display_path(log path)>`. Logs live under the Git common directory (`log_path`, `run.py:446`), which is `.git` inside the main checkout in the usual layout.

Worktrees are created under `<main checkout>/.worktrees/` (`run.py:493`, `run.py:1215`). Update every existing test that matches `Running check` or parses the `log:` line as an absolute path: `tests/test_run_progress.py` (lines 12 and 26), `tests/test_next.py:1335`, `tests/test_run_log.py` (`one_log`, about lines 73-80) and `tests/test_review_rebase_session.py` (about lines 96-102). Resolve the relative `log:` path against the main checkout in those helpers.

Out of scope: other runner messages.

## Acceptance Criteria

- [ ] A Hypothesis property test (`@given` on a `unittest.TestCase` method, as in `tests/test_property_landing_paths.py`) in a new file `tests/test_property_display_path.py`, importing `from chitty.run import display_path`, draws `main_root` as `/` joined with 1 to 3 non-empty segments, and further non-empty segments (letters including non-ASCII, spaces; never `.` or `..`). Inside paths are `main_root` joined with 0 or more segments; outside paths include a sibling `main_root.with_name(main_root.name + "-x")` with segments, a root under a different first segment, and an unresolved alias that names a path inside `main_root` only after resolving `..` (`main_root.parent / "z" / ".." / main_root.name / "seg"`). It asserts an inside path gives a relative string with `main_root / result == path` (`.` for `main_root` itself); every other path gives `str(path)`. A string-prefix or resolving implementation fails.
- [ ] `tests/test_run_progress.py` asserts the review-mode check line is exactly `TASK-1: running check in .worktrees/task-1...` (with `task-1` the worktree name the fixture creates); this assertion fails on `main` today.
- [ ] In `tests/test_run_progress.py` on `ReviewMergeTestCase`, a test asserts that the `log:` line printed after a review run is relative and starts `.git/chitty/run/TASK-1-`; it fails on `main`.

## Plan

Add display_path and use it for check and log progress; add property and integration regression tests, update path consumers, and run checks.

## Notes

Suggestion origin: taidy

Regression: pytest tests/test_run_progress.py -q fails all three tests before the fix, including the exact check line and relative log assertions.

Property regression: pytest tests/test_property_display_path.py -q fails with display_path replaced by str(path), and passes with the implementation. Integration regressions also failed before the fix.

Reviewed: Complete diff inspected; no prior review findings or Decided note. `make check` passed: 1145 tests, 791 subtests.
1: pass - `make check` passed the property test; on the merge base, `PYTHONPATH=src ../../.venv/bin/python -m pytest tests/test_property_display_path.py -q` failed collection with `ImportError: cannot import name display_path`.
2: pass - `make check` passed the exact review progress assertion; on the merge base `PYTHONPATH=src ../../.venv/bin/python -m pytest tests/test_run_progress.py -q` failed with `ValueError` for the missing exact line.
3: pass - `make check` passed the relative log assertion; the same merge-base progress test failed with `AssertionError: False is not true` for the log prefix.

## Summary

Implemented relative runner check and log paths with property and review integration coverage. make check passed (1144 tests); regression tests failed before the fix.

## History

- 2026-11-23T10:24:04Z witty-russet-gannet → backlog
- 2026-11-23T10:24:05Z witty-russet-gannet: changed notes
- 2026-11-23T10:30:28Z witty-russet-gannet: changed title, description, acceptance criteria
- 2026-11-23T10:30:28Z witty-russet-gannet backlog → planning
- 2026-11-23T10:30:36Z witty-russet-gannet: changed description
- 2026-11-23T10:30:36Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:33:03Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:33:03Z witty-russet-gannet cold-read → planning
- 2026-11-23T10:33:07Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:35:09Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:35:09Z witty-russet-gannet cold-read → planning
- 2026-11-23T10:35:11Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:35:25Z witty-russet-gannet: changed acceptance criteria
- 2026-11-23T10:35:25Z witty-russet-gannet cold-read → planning
- 2026-11-23T10:35:27Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:36:56Z witty-russet-gannet cold-read → todo
- 2026-11-23T10:37:12Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T11:04:24Z able-coral-marten todo → doing
- 2026-11-23T11:07:24Z able-coral-marten: wrote the plan
- 2026-11-23T11:07:48Z able-coral-marten: changed notes
- 2026-11-23T11:10:31Z able-coral-marten: changed notes
- 2026-11-23T11:12:45Z able-coral-marten: changed summary
- 2026-11-23T11:12:45Z able-coral-marten doing → review
- 2026-11-23T11:21:47Z rosy-quartz-newt: changed notes
- 2026-11-23T11:21:47Z rosy-quartz-newt review → done
