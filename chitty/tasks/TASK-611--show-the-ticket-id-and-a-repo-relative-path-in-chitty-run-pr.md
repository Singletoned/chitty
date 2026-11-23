---
title: Show the ticket ID and a repo-relative path in `chitty run` progress lines
status: planning
created: 2026-11-23
---

## Description

`chitty run` prints `Running check in <absolute worktree path>...` (`_run_check`, `src/chitty/run.py:1463`). In a narrow terminal the useful part, the ticket worktree name, is cut off, and the line does not say which ticket it is for. Seen in taidy, 2026-11-22: `Running check in /Users/.../taidy/.worktrees/task-4...`. The `log: <path>` line printed at the end of a run (`run.py:475`) has the same problem.

Change:

- Add a pure function `display_path(path: Path, main_root: Path) -> str` to `run.py`: the path relative to `main_root` when it is inside it, otherwise `str(path)` unchanged.
- The check line becomes `<ID>: running check in <display_path(worktree)>...`, for example `TASK-4: running check in .worktrees/task-4...`.
- The log line becomes `log: <display_path(log path)>`. Logs live under the Git common directory (`log_path`, `run.py:446`), which is `.git` inside the main checkout in the usual layout.

Worktrees are created under `<main checkout>/.worktrees/` (`run.py:493`, `run.py:1215`). Update the existing assertions in `tests/test_run_progress.py` that match the old wording.

Out of scope: other runner messages.

## Acceptance Criteria

- [ ] A Hypothesis property test of `display_path(path, main_root)` draws path segments (including spaces and non-ASCII letters) and builds paths both inside and outside `main_root`; it asserts that a path inside gives a relative string with `main_root / result == path`, and a path outside gives `str(path)`.
- [ ] `tests/test_run_progress.py` asserts the review-mode check line is exactly `TASK-1: running check in .worktrees/task-1...` (with `task-1` the worktree name the fixture creates); this assertion fails on `main` today.
- [ ] A test asserts that the `log:` line `chitty run` prints after a run names a path relative to the main checkout, starting `.git/chitty/run/TASK-1-`.

## Notes

Suggestion origin: taidy

## History

- 2026-11-23T10:24:04Z witty-russet-gannet → backlog
- 2026-11-23T10:24:05Z witty-russet-gannet: changed notes
- 2026-11-23T10:30:28Z witty-russet-gannet: changed title, description, acceptance criteria
- 2026-11-23T10:30:28Z witty-russet-gannet backlog → planning
