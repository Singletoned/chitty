---
title: Runner error notes need a blank line before their code fences
status: review
created: 2026-11-22
---

## Description

Runner error notes put a fenced code block straight after a text line, which
Prettier rewrites with a blank line between them. In taidy (2026-11-22) a
TASK-21 note `Error output:` followed directly by a ```` ```text ```` fence
failed the project's `prettier --check`, so the runner errored the ticket
again because of its own note.

Change: in `_runner_error_note` (`src/chitty/run.py` around line 1402), write
`"\n\nError output:\n\n"` before the `code_block(...)`, not
`"\n\nError output:\n"`. It is the only `code_block` caller
(`grep -n "code_block(" src/chitty/*.py`). Update the expected string in
`tests/test_property_runner_error_note.py` line 30 to match.

Test: add to `tests/test_property_runner_error_note.py` an exact-string
test: `_runner_error_note("check", "first\nsecond", Path("/w"))` equals
``'Runner error (check): first\n\nWorktree: `/w`\n\nError output:\n\n```text\nsecond\n```'``.
Record that it fails before the change. The existing property (line 30)
mirrors the implementation, so it is not evidence on its own.

## Acceptance Criteria

- [ ] A runner error note with extra output has a blank line between `Error output:` and the fence; shown by the new exact-string test, which fails before the change.
- [ ] `make check` passes.

## Plan

Add the exact-string regression test and verify it fails, then fix the separator and property expectation, run make check, and commit.

## Notes

Suggestion origin: taidy

Cold read: test made exact-string; nothing else serious.

The exact-string regression test failed before the fix: the actual note lacks the blank line before the fence.

## Summary

Added blank line before error output fences and an exact-string regression test. Confirmed the test failed before the fix; make check passed.

## History

- 2026-11-22T13:16:25Z friendly-jade-stoat → backlog
- 2026-11-22T13:16:25Z friendly-jade-stoat: changed notes
- 2026-11-22T13:18:36Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T13:18:36Z friendly-jade-stoat backlog → planning
- 2026-11-22T13:20:23Z friendly-jade-stoat: changed description, acceptance criteria, notes
- 2026-11-22T13:20:23Z friendly-jade-stoat planning → todo
- 2026-11-22T15:34:00Z mellow-amber-marten todo → doing
- 2026-11-22T15:36:52Z mellow-amber-marten: wrote the plan
- 2026-11-22T15:37:05Z mellow-amber-marten: changed notes
- 2026-11-22T15:40:41Z mellow-amber-marten: changed summary
- 2026-11-22T15:44:05Z mellow-amber-marten doing → review
