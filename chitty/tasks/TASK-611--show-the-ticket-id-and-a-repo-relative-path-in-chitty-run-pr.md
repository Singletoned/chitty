---
title: Show the ticket ID and a repo-relative path in `chitty run` progress lines
status: cold-read
created: 2026-11-23
---

## Description

`chitty run` prints `Running check in <absolute worktree path>...` (`_run_check`, `src/chitty/run.py:1463`). In a narrow terminal the useful part, the ticket worktree name, is cut off, and the line does not say which ticket it is for. Seen in taidy, 2026-11-22: `Running check in /Users/.../taidy/.worktrees/task-4...`. The `log: <path>` line printed at the end of a run (`run.py:475`) has the same problem.

Change:

- Add a pure function `display_path(path: Path, main_root: Path) -> str` to `run.py`: the path relative to `main_root` when it is inside it, otherwise `str(path)` unchanged. Compare the paths as given, without resolving symlinks or `..`; the main root and Git common dir are resolved (`git.main_checkout`, `git_common_dir`); worktree paths come from `main_root / ".worktrees"` or from `git worktree list`, which prints real paths. Criterion 2 checks the printed form end to end. `path == main_root` gives `.`. A log under a Git directory outside the main checkout (separate git dir) is printed absolute; that fallback is intended. For the check line, pass `main_root` (already in scope in `_run_ticket_with_log`, about `run.py:488`) into `_run_check` as a parameter. For the `log:` line, use `main_repo.root` (in scope in `_run_ticket`, `run.py:475`). In `tests/test_next.py:1335`, match `running check in`.
- The check line becomes `<ID>: running check in <display_path(worktree)>...`, for example `TASK-4: running check in .worktrees/task-4...`.
- The log line becomes `log: <display_path(log path)>`. Logs live under the Git common directory (`log_path`, `run.py:446`), which is `.git` inside the main checkout in the usual layout.

Worktrees are created under `<main checkout>/.worktrees/` (`run.py:493`, `run.py:1215`). Update every existing test that matches `Running check` or parses the `log:` line as an absolute path: `tests/test_run_progress.py` (lines 12 and 26), `tests/test_next.py:1335`, `tests/test_run_log.py` (`one_log`, about lines 73-80) and `tests/test_review_rebase_session.py` (about lines 96-102). Resolve the relative `log:` path against the main checkout in those helpers.

Out of scope: other runner messages.

## Acceptance Criteria

- [ ] A Hypothesis property test in a new file `tests/test_display_path.py` (importing `from chitty.run import display_path`) draws `main_root` as `/` joined with 1 to 3 drawn segments, and further segments (letters including non-ASCII, spaces; never `.` or `..`). Inside paths are `main_root` joined with 0 or more segments; outside paths include a sibling `main_root.with_name(main_root.name + "-x")` with segments, unrelated roots, and an unresolved alias that names a path inside `main_root` only after resolving `..` (`main_root.parent / "z" / ".." / main_root.name / "seg"`). It asserts an inside path gives a relative string with `main_root / result == path` (`.` for `main_root` itself); every other path gives `str(path)`. A string-prefix or resolving implementation fails.
- [ ] `tests/test_run_progress.py` asserts the review-mode check line is exactly `TASK-1: running check in .worktrees/task-1...` (with `task-1` the worktree name the fixture creates); this assertion fails on `main` today.
- [ ] In `tests/test_run_progress.py` on `ReviewMergeTestCase`, a test asserts that the `log:` line printed after a review run is relative and starts `.git/chitty/run/TASK-1-`; it fails on `main`.

## Notes

Suggestion origin: taidy

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
