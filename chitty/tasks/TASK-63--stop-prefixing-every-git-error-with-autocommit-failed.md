---
title: Stop prefixing every Git error with `autocommit failed`
status: doing
created: 2026-10-30
---

## Description

`_git` in `src/chitty/git.py` (defined at line 418) starts every error with `autocommit failed`, whatever Git command failed. Most of its callers have nothing to do with autocommit: `file_at`, `_git_path`, ID allocation, the clean-tree check for `chitty import`, and source removal. So a user sees a misleading cause.

Change the message in `_git` to name the command without blaming autocommit:

    `git rev-parse --verify no-such-ref` failed in /path/to/repo:
    fatal: Needed a single revision

That is, `f"`{shown}` failed in {root}:\n{stderr}"`, with `shown` and `stderr` as they are now.

`git.commit` (`src/chitty/git.py:21`) is the one caller that really is autocommit: all four of its callers in `store.py` make Chitty's automatic commits. Keep its context there. Its `except ChittyError:` around the `git commit` call already restores the index and re-raises; change the bare `raise` to `raise ChittyError(f"autocommit failed: {error}") from error`, binding the exception as `error`. So a failing pre-commit hook reads `autocommit failed: `git commit ...` failed in ...` followed by the hook's output.

Leave the message at `git.py:393` (`autocommit failed restoring the Git index`) alone: it is an autocommit failure.

Two existing tests assert `autocommit failed` for a failing pre-commit hook: `tests/test_autocommit.py:288` and `tests/test_cli.py:576`. Leave them unchanged: they must still pass, which shows the commit path kept its context.

Out of scope: autocommit context for the other Git calls inside `git.commit` (`ls-files`, `diff`, `add`, and the `reset` and `_apply_cached` in its handler), which will name only the Git command; shortening the multi-line commit message that `shown` includes for a failed `git commit`, the `cannot confirm a clean Git working tree` wrapper in `require_clean`, and any other error text.

## Acceptance Criteria

- [ ] A new test in `tests/test_git.py`, in a repository with one commit, makes `git.file_at` fail on a ref that does not exist and asserts the error contains `` `git rev-parse --verify no-such-ref` failed in `` and does not contain `autocommit`; the worker records that it failed before the fix
- [ ] The two pre-commit hook tests (`tests/test_autocommit.py:288`, `tests/test_cli.py:576`) pass unchanged, and `make check` passes

## Plan

Update _git to report the failed Git command directly, then wrap only git.commit failures with the autocommit context. Add the missing-ref regression test in tests/test_git.py, first run it against the current code to verify it fails, then run make check and record verification.

## Notes

Cold read by a fresh Haiku subagent, 2026-11-07, kept as `refs/cold-read/TASK-63/1`. It built the first version from the description alone: the new test failed first, then passed, and `make check` passed. Outcomes:

- Fixed, serious: the first version also stripped the context from real autocommit failures, because `git.commit` goes through `_git`. A failing hook then said only `` `git commit --quiet --only -m chitty: add ...` failed ``. Now `git.commit` wraps its failure in `autocommit failed: ...`, and the two hook tests stay unchanged to prove it.
- Fixed: criterion 1 now says the repository has one commit, so the test shows the missing ref is the cause.
- Rejected: "line 418 should be 423". 418 is where `_git` is defined, and the description now says so.
- Rejected: `require_clean` already wraps the error in `cannot confirm a clean Git working tree`, so it keeps its context; listed as out of scope.
- Rejected: archived `TASK-62` quotes the old prefix; archived tickets are history and stay as written.
- The commit-path fix changes the design, so a second read follows.

Second cold read by a fresh Haiku subagent, 2026-11-07, kept as `refs/cold-read/TASK-63/2`. The new test failed first for the right reason, `make check` passed, and with only the `_git` change both hook tests failed, so criterion 2 does guard the commit path. Hook output after the fix: ``Error: autocommit failed: `git commit --quiet --only -m chitty: add TASK-1 X ...` failed in ...:`` then `nope`. Nothing serious. Outcomes:

- Fixed: the `git.commit` line number, now `git.py:21`.
- Fixed: criterion 1 now names `tests/test_git.py`.
- Rejected, now stated as out of scope: wrapping the other Git calls inside `git.commit`. A stale `index.lock` gives ``Error: `git add -- ...` failed in ...: fatal: Unable to create ... index.lock``, which already names the command and the cause, and wrapping the whole body, handler included, is more change than this ticket needs.
- Rejected: "failed" appearing twice in the hook message. It reads clearly.

## History

- 2026-10-30 → backlog
- 2026-11-07T09:16:05Z vivid-dormouse: changed description, acceptance criteria
- 2026-11-07T09:21:04Z vivid-dormouse: changed description, acceptance criteria, notes
- 2026-11-07T09:26:03Z vivid-dormouse: changed description, acceptance criteria, notes
- 2026-11-07T09:26:03Z vivid-dormouse backlog → todo
- 2026-11-07T09:26:11Z vivid-dormouse: changed acceptance criteria
- 2026-11-08T09:34:54Z kind-urchin todo → doing
- 2026-11-08T09:49:16Z kind-urchin: wrote the plan
