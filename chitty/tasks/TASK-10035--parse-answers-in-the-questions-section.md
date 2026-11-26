---
title: Parse answers in the `## Questions` section
status: doing
depends_on:
  - TASK-629
parent: TASK-621
created: 2026-11-26
---

## Description

Part of TASK-621. TASK-629 parses `## Questions` items in `src/chitty/model.py` (`_parse_questions`, `Question`, `Task.questions`), with `answer` always `None`. This ticket parses answers.

Format (the layout that both the pinned prettier and mdformat leave unchanged):

```markdown
## Questions

- [x] Which database?

  Postgres, because we already run it.

- [ ] Who owns the migration?
```

Rules, in `_parse_questions`:

- An answer is one paragraph: indented lines (first character a space or tab) after an item and one or more blank lines, up to the next item or the end of the section, joined with a space and stripped of their indent. Whitespace-only lines count as blank.
- After an answer, a further indented paragraph raises `TaskError` `question <n>: an answer must be one paragraph`.
- The tick and the answer are independent: `[x]` with no answer and `[ ]` with an answer both parse.

Tests, added to `tests/test_questions_section.py`:

- The example above gives `(Question(True, "Which database?", "Postgres, because we already run it."), Question(False, "Who owns the migration?", None))`, and `render()` returns the text unchanged.
- `- [ ] Q\n\n  Part one\n\tpart two\n` gives answer `"Part one part two"`; a `"   "` line in place of the blank line gives the same.
- The one-paragraph refusal, with its exact message.
- In `tests/test_formatters.py`, add `task = task.with_section(QUESTIONS, <the example section body>)` inside `sample()`, next to its existing `with_section("Plan", ...)` call, so the prettier and mdformat tests cover it.
- Renumbering: `parse` the text `"---\ntitle: T\nstatus: todo\ncreated: 2026-11-23\n---\n\n## Description\n\nD.\n\n## Acceptance Criteria\n\n- [ ] A\n\n## Questions\n\n- [ ] Does TASK-7 block TASK-70?\n\n  Yes, see TASK-7.\n"` and call `chitty.renumbering.rewrite_task(task, {TaskId("TASK", 7): TaskId("TASK", 12)})`. Its `questions` is `(Question(False, "Does TASK-12 block TASK-70?", "Yes, see TASK-12."),)`. (`rewrite_task` loops over `SECTION_ORDER`, which includes `QUESTIONS` after TASK-629, and rewrites every section except History and Acceptance Criteria; this checks it reaches answers.)

Each answer and refusal test fails before the change with the `may only contain` error from TASK-629.

Out of scope: `as_dict` (TASK-649), `chitty show` (TASK-650), CLI and MCP options (TASK-630).

## Acceptance Criteria

- [x] The answer, refusal, formatter and renumbering tests pass; each answer and refusal test fails before the change, with the failure recorded in a note
- [x] `make check` passes

## Plan

Add focused parsing, refusal, round-trip, formatter and renumbering tests; record their failures before implementing answer-paragraph tracking in the questions parser. Format, run make check, and hand off for review.

## Notes

Before the fix, .venv/bin/pytest -q tests/test_questions_section.py -k answer_or_renumber (using the expression answer or renumber) failed the example, both blank-line variants, renumbering, and refusal: each received the may only contain error.

## Summary

Parse single-paragraph answers independently of question ticks, preserving round trips and renumbering. Added formatter and parsing coverage; make check passes.

## History

- 2026-11-26T11:27:21Z brisk-bronze-adder → planning
- 2026-11-26T11:28:48Z brisk-bronze-adder planning → cold-read
- 2026-11-26T11:29:54Z brisk-bronze-adder: changed description
- 2026-11-26T11:29:54Z brisk-bronze-adder cold-read → planning
- 2026-11-26T11:30:04Z brisk-bronze-adder planning → todo
- 2026-11-26T11:30:23Z brisk-bronze-adder: changed description
- 2026-11-26T13:54:31Z upbeat-zinc-wren todo → doing
- 2026-11-26T13:58:30Z upbeat-zinc-wren: wrote the plan
- 2026-11-26T13:59:00Z upbeat-zinc-wren: changed notes
- 2026-11-26T14:02:07Z upbeat-zinc-wren: changed summary; ticked acceptance criteria
