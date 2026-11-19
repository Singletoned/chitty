---
title: Raise on `git` failures other than "not a git repository" in `git.is_repository`
status: planning
depends_on:
  - TASK-405
created: 2026-11-19
---

## Description

`git.is_repository` (`src/chitty/git.py:371`) returns `result.returncode == 0 and result.stdout.strip() == "true"`, so every non-zero exit of `git rev-parse --is-inside-work-tree` reads as a folder outside Git. Only one of those exits means that: status 128 with `not a git repository` in standard error. Others, such as Git refusing a repository with `detected dubious ownership` (also status 128), a permission error or a corrupt `.git`, are hidden, and callers silently skip committing.

Decisions:

- Take the decision out into a pure function in `src/chitty/git.py`: `repository_answer(command: Sequence[str], directory: Path, returncode: int, stdout: str, stderr: str) -> bool`. It returns `True` for status 0 with standard output `true`, `False` for status 0 with any other output, `False` for status 128 when standard error contains `not a git repository`, and otherwise raises `ChittyError` containing the command, `directory` and the stripped standard error, in the style of `_git` (`src/chitty/git.py:656`).
- `is_repository` runs `git` with `LC_ALL=C` added to the environment so the message is English, and returns `repository_answer(...)`.
- `TASK-405`'s handling of a missing directory or missing `git` stays as it is.

Tests go in `tests/test_git.py`. The repository's property-testing tool is Hypothesis.

## Acceptance Criteria

- [ ] Property test of `repository_answer`, generated with Hypothesis: draw the status from 0, 1, 128, 129 and any integer from 1 to 255; standard output from `true`, `false`, the empty string and drawn text, each with optional surrounding whitespace; standard error as drawn text, optionally containing `not a git repository` at a drawn position. The result is `True` exactly when the status is 0 and the stripped output is `true`; `False` when the status is 0 otherwise, or 128 with the phrase; for every other case it raises `ChittyError` whose message contains the stripped standard error and the directory.
- [ ] Example test with real Git: `is_repository` on a repository whose `.git/HEAD` is overwritten with `garbage` raises `ChittyError` containing the standard error `git` printed. It fails on `main`, which returns `False`. A plain temporary directory outside any repository still returns `False` with `LANG` set to `de_DE.UTF-8` in the environment.
- [ ] `make check` passes.

## History

- 2026-11-19T08:43:27Z lively-quartz-crane → planning
