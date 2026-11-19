---
title: Raise on `git` failures other than "not a git repository" in `git.is_repository`
status: planning
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

- [ ] Property test of `repository_answer`, generated with Hypothesis, each case built so its answer is known, with `directory` a drawn resolved path whose `str` the message must contain. Draw a kind. Inside: status 0, output `true` with surrounding whitespace that `str.strip()` removes, answer `True`. Outside-output: status 0, output sampled from `false`, `True`, `TRUE`, `truex`, `xtrue`, `true false`, the empty string, or drawn text whose stripped form is not `true`, answer `False`. Not-a-repository: status 128, standard error containing the lowercase `not a git repository` at a drawn position, answer `False`. Other-failure: raises `ChittyError` containing the stripped standard error and `str(directory)`; status drawn from -64 to 255 excluding 0, with 128 always among the drawn cases, and non-empty standard error lacking the phrase; or any such status other than 128 with the phrase; or 128 with `Not a git repository` or `NOT A GIT REPOSITORY`. The phrase match is case-sensitive.
- [ ] Evidence, recorded in a note: each of these wrong versions of `repository_answer` fails a criterion 1 test: case-insensitive phrase match; `"true" in stdout`; status ignored; status 128 always `False`; phrase ignored. Separately, a Hypothesis test drawing any integer status and any text for both streams shows the function only returns a `bool` or raises `ChittyError`.
- [ ] Example tests through `is_repository`: a real repository whose `.git/config` sets `repositoryformatversion = 99` raises `ChittyError` containing `found 99` (fails on `main`, which returns `False`). A plain temporary directory with `PATH` set to a directory holding only an executable `git` shell script that, unless `LC_ALL` is `C`, prints `Schwerwiegend: Kein Git-Repository` to standard error, and otherwise prints `fatal: not a git repository`, both with status 128: `is_repository` returns `False` with `LC_ALL` removed from the environment and `LANG=de_DE.UTF-8` set. Without `LC_ALL=C` the call raises, so this fails on a version that omits it.
- [ ] `make check` passes.

## History

- 2026-11-19T08:43:27Z lively-quartz-crane → planning
- 2026-11-19T08:43:53Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-19T08:47:04Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:48:59Z lively-quartz-crane: changed description
- 2026-11-19T08:49:15Z lively-quartz-crane cold-read → planning
- 2026-11-19T08:49:17Z lively-quartz-crane: changed acceptance criteria
