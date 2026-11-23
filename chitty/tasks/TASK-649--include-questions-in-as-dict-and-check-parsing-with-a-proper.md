---
title: Include `## Questions` in `as_dict` and check parsing with a property test
status: cold-read
depends_on:
  - TASK-629
parent: TASK-621
created: 2026-11-23
---

## Description

Part of TASK-621. TASK-629 parses `## Questions` into `Task.questions` (the format and the `Question` dataclass are described there). This ticket adds the questions to `Task.as_dict` in `src/chitty/model.py`, so `chitty show --json` and the MCP tools carry them, and checks parsing with a property test.

Code:

- `as_dict` adds `"questions": [{"index": n, "checked": ..., "text": ..., "answer": ...}]`, numbered from 1, as `acceptance_criteria` is; `answer` is `null` when there is none. It is an empty list when there is no section.

Tests, in `tests/test_questions_section.py` (created by TASK-629):

- Example: for the two-question example in TASK-629, `as_dict()["questions"]` is `[{"index": 1, "checked": True, "text": "Which database?", "answer": "Postgres, because we already run it."}, {"index": 2, "checked": False, "text": "Who owns the migration?", "answer": None}]`; for a ticket with no `## Questions` section it is `[]`.
- Property, with Hypothesis and `examples(50)` from `tests/__init__.py`: build Questions bodies from one to five items, each with a drawn tick (` `, `x`, `X`), text of one to three words of `string.ascii_letters` joined by single spaces (so no leading or trailing space), an optional continuation line, and an optional answer: one or two indented lines with no blank line between them, after the item (or its continuation line) and one or two blank lines. Items are separated by one or two blank lines. Each indented line draws its indent from two spaces, four spaces and a tab. Then `parse` succeeds, `render()` is byte-identical, and `as_dict()["questions"]` has one entry per item, with the drawn tick, text and answer (text and answer as their lines joined with single spaces).
- Both tests fail before the change with `KeyError: 'questions'`, because `parse` already succeeds after TASK-629.

Out of scope: `chitty show` text output (TASK-C) and CLI and MCP options (TASK-630).

## Acceptance Criteria

- [ ] The example and property tests in `tests/test_questions_section.py` pass, and each fails before the change with `KeyError: 'questions'`; record the failure messages in a note
- [ ] `make check` passes

## History

- 2026-11-23T19:43:19Z friendly-coral-badger → planning
- 2026-11-23T19:43:54Z friendly-coral-badger planning → cold-read
