---
title: Stop prefixing every Git error with `autocommit failed`
status: backlog
created: 2026-10-30
---

## Description

`_git` in `src/chitty/git.py` (line 418) starts every error with `autocommit failed`, whatever Git command failed. Most of its callers have nothing to do with autocommit: `file_at`, `_git_path`, ID allocation, the clean-tree check for `chitty import`, and source removal. So a user sees a misleading cause.

Change the message in `_git` to name the command without blaming autocommit:

    `git rev-parse --verify no-such-ref` failed in /path/to/repo:
    fatal: Needed a single revision

That is, `f"`{shown}` failed in {root}:\n{stderr}"`, with `shown` and `stderr` as they are now.

Leave the message at `git.py:393` (`autocommit failed restoring the Git index`) alone: it is an autocommit failure.

Two existing tests assert the old wording for a failing pre-commit hook: `tests/test_autocommit.py:288` and `tests/test_cli.py:576`. Change them to assert `` `git commit `` and `failed` instead.

Out of scope: wrapping autocommit's own `git commit` failure in a separate autocommit message, and any other error text.

## Acceptance Criteria

- [ ] A new test makes `git.file_at` fail on a ref that does not exist and asserts the error contains `` `git rev-parse --verify no-such-ref` failed in `` and does not contain `autocommit`; the worker records that it failed before the fix
- [ ] The two pre-commit hook tests assert the new wording, and `make check` passes

## History

- 2026-10-30 → backlog
- 2026-11-07T09:16:05Z vivid-dormouse: changed description, acceptance criteria
