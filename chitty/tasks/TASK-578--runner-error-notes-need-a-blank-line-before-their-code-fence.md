---
title: Runner error notes need a blank line before their code fences
status: planning
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

Test: add to `tests/test_property_runner_error_note.py` a test that builds a
note with `_runner_error_note("check", "first\nsecond", Path("/w"))` and
asserts the line before the opening fence is empty. Record that it fails
before the change.

## Acceptance Criteria

- [ ] A runner error note with extra output has a blank line between `Error output:` and the fence; shown by the new test, which fails before the change.
- [ ] `make check` passes.

## Notes

Suggestion origin: taidy

## History

- 2026-11-22T13:16:25Z friendly-jade-stoat → backlog
- 2026-11-22T13:16:25Z friendly-jade-stoat: changed notes
- 2026-11-22T13:18:36Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T13:18:36Z friendly-jade-stoat backlog → planning
