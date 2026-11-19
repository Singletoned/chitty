---
title: Add `git.repository_answer` to classify `git rev-parse --is-inside-work-tree` results
status: doing
created: 2026-11-19
---

## Description

`git.is_repository` (`src/chitty/git.py:371`) returns `result.returncode == 0 and result.stdout.strip() == "true"`, so every non-zero exit of `git rev-parse --is-inside-work-tree` reads as a folder outside Git. Only one of those exits means that: status 128 with `not a git repository` in standard error. Others are hidden, such as `detected dubious ownership`, `unable to access '.git/config': Permission denied` or `Expected git repo version <= 1, found 99` (all status 128), and callers silently skip committing.

This ticket adds only the decision, as a pure function; `TASK-407` makes `is_repository` use it.

Add to `src/chitty/git.py`: `repository_answer(command: Sequence[str], directory: Path, returncode: int, stdout: str, stderr: str) -> bool`.

- Status 0: `True` when `stdout.strip()` is `true`, otherwise `False`. Standard error is ignored.
- Status 128 with standard error containing `not a git repository` (case-sensitive; `TASK-407` forces English output): `False`.
- Anything else, including negative statuses (a signal killed `git`) and status 128 with empty standard error: raise `ChittyError` containing the command, `str(directory)` and the stripped standard error, in the style of `_git` (`src/chitty/git.py:656`).

Tests go in `tests/test_git.py`. The repository's property-testing tool is Hypothesis. Before writing the function, add it raising `NotImplementedError` so the tests fail on their own.

## Acceptance Criteria

- [ ] Property test, Hypothesis, status 0: standard output `true` padded with whitespace that `str.strip()` removes gives `True`; output sampled from `false`, `True`, `TRUE`, `truex`, `xtrue`, `true false`, the empty string, or drawn text whose stripped form is not `true`, gives `False`. Standard error is drawn text in both.
- [ ] Property test, Hypothesis, non-zero status: status 128 with standard error made of the lowercase `not a git repository` between two drawn texts (either may be empty) gives `False`. Every other case raises `ChittyError` containing the command as `_git` shows it (`` `git rev-parse --is-inside-work-tree` ``), `str(directory)` for a drawn `directory`, and the stripped standard error: status drawn from -64 to 255 excluding 0, with 128 always among the cases, and standard error drawn text filtered to lack the phrase (empty allowed, which checks only the command and directory); status other than 128 with the phrase; 128 with `Not a git repository` or `NOT A GIT REPOSITORY`. Standard output is drawn from `true`, padded `true` and drawn text in every case.
- [ ] Evidence, recorded in a note: the tests failed against the `NotImplementedError` stub, and each wrong version, implemented and run, fails a test from criteria 1 or 2: case-insensitive phrase match; `"true" in stdout`; `True` whenever stripped output is `true`, whatever the status; status 128 gives `False` without checking the phrase; any non-zero status gives `False`; message without the command. A Hypothesis test drawing the status from `st.integers()` and both streams from `st.text()` shows the function only returns a `bool` or raises `ChittyError`.
- [ ] `make check` passes.

## Plan

Add Hypothesis property tests for repository_answer, first proving they fail with a NotImplementedError stub. Implement the pure result classifier with exact status/stdout/stderr rules and _git-style errors. Exercise the specified wrong variants and broad status/stream generation, then run make format and make check and commit implementation with a Task trailer.

## History

- 2026-11-19T08:43:27Z lively-quartz-crane → planning
- 2026-11-19T08:43:53Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-19T08:47:04Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:48:59Z lively-quartz-crane: changed description
- 2026-11-19T08:49:15Z lively-quartz-crane cold-read → planning
- 2026-11-19T08:49:17Z lively-quartz-crane: changed acceptance criteria
- 2026-11-19T08:49:37Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:51:02Z lively-quartz-crane cold-read → planning
- 2026-11-19T08:51:05Z lively-quartz-crane: changed title, description, acceptance criteria
- 2026-11-19T08:51:25Z lively-quartz-crane: changed dependencies
- 2026-11-19T08:51:30Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:52:50Z lively-quartz-crane cold-read → planning
- 2026-11-19T08:52:52Z lively-quartz-crane: changed acceptance criteria
- 2026-11-19T08:52:52Z lively-quartz-crane planning → todo
- 2026-11-19T08:56:36Z youthful-pearl-eel todo → doing
- 2026-11-19T08:57:51Z youthful-pearl-eel: wrote the plan
