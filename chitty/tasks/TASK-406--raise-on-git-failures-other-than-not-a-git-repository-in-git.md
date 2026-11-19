---
title: Raise on `git` failures other than "not a git repository" in `git.is_repository`
status: cold-read
depends_on:
  - TASK-405
created: 2026-11-19
---

## Description

`git.is_repository` (`src/chitty/git.py:371`) returns `result.returncode == 0 and result.stdout.strip() == "true"`, so every non-zero exit of `git rev-parse --is-inside-work-tree` reads as a folder outside Git. Only one of those exits means that: status 128 with `not a git repository` in standard error. Others are hidden, such as `detected dubious ownership`, `unable to access '.git/config': Permission denied` or `Expected git repo version <= 1, found 99` (all status 128), and callers silently skip committing.

Decisions:

- Take the decision out into a pure function in `src/chitty/git.py`: `repository_answer(command: Sequence[str], directory: Path, returncode: int, stdout: str, stderr: str) -> bool`. It returns `True` for status 0 with standard output `true`, `False` for status 0 with any other output, `False` for status 128 when standard error contains `not a git repository`, and otherwise raises `ChittyError` containing the command, `directory` and the stripped standard error, in the style of `_git` (`src/chitty/git.py:656`).
- `is_repository` runs `git` with `LC_ALL=C` added to the environment so the message is English, and returns `repository_answer(...)`.
- `TASK-405`'s handling of a missing directory or missing `git` stays as it is. `is_repository` passes `repository_answer` the resolved directory that `TASK-405` introduces.
- Negative statuses (a signal killed `git`) are other failures and raise.

Tests go in `tests/test_git.py`. The repository's property-testing tool is Hypothesis.

## Acceptance Criteria

- [ ] Property test of `repository_answer`, generated with Hypothesis, with each case built so its answer is known: draw a kind (inside, outside-output, not-a-repository, other-failure). Inside: status 0, standard output `true` with optional surrounding whitespace, answer `True`. Outside-output: status 0, output drawn from `false`, the empty string or text whose stripped form is not `true`, answer `False`. Not-a-repository: status 128, standard error containing `not a git repository` at a drawn position, answer `False`. Other-failure: status drawn from 1 to 255 with standard error drawn text without the phrase, or any non-zero status other than 128 with the phrase; it raises `ChittyError` whose message contains the stripped standard error and the directory.
- [ ] Example tests with real Git: a repository whose `.git/config` sets `repositoryformatversion = 99` makes `is_repository` raise `ChittyError` containing `found 99`; it fails on `main`, which returns `False`. A plain temporary directory outside any repository returns `False` with `LANG=de_DE.UTF-8` and `LC_ALL` unset in the environment; without `LC_ALL=C` Git prints `Kein Git-Repository` there.
- [ ] `make check` passes.

## History

- 2026-11-19T08:43:27Z lively-quartz-crane → planning
- 2026-11-19T08:43:53Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-19T08:47:04Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:48:59Z lively-quartz-crane: changed description
