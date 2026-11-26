---
title: Parse answers in the `## Questions` section
status: planning
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
- After an answer, a further indented paragraph raises `TaskError` `question <n>: an answer must be one paragraph`. An indented line whose stripped text matches `LIST_MARKER_RE` raises `question <n>: nested lists are not allowed`.
- The tick and the answer are independent: `[x]` with no answer and `[ ]` with an answer both parse.

Tests, added to `tests/test_questions_section.py`:

- The example above gives `(Question(True, "Which database?", "Postgres, because we already run it."), Question(False, "Who owns the migration?", None))`, and `render()` returns the text unchanged.
- `- [ ] Q\n\n  Part one\n\tpart two\n` gives answer `"Part one part two"`; a `"   "` line in place of the blank line gives the same.
- The two refusals, with their exact messages.
- In `tests/test_formatters.py`, give `sample()` the example section (through `with_section`), so the prettier and mdformat tests cover it.
- Renumbering: parse a ticket whose Questions section is `- [ ] Does TASK-7 block TASK-70?`, a blank line, then `  Yes, see TASK-7.`, and call `chitty.renumbering.rewrite_task(task, {TaskId("TASK", 7): TaskId("TASK", 12)})`. Its `questions` is `(Question(False, "Does TASK-12 block TASK-70?", "Yes, see TASK-12."),)`. (`rewrite_task` already rewrites every section except History and Acceptance Criteria; this checks it reaches answers.)

Each answer and refusal test fails before the change with the `may only contain` error from TASK-629.

Out of scope: `as_dict` (TASK-649), `chitty show` (TASK-650), CLI and MCP options (TASK-630).

## Acceptance Criteria

- [ ] The answer, refusal, formatter and renumbering tests pass; each answer and refusal test fails before the change, with the failure recorded in a note
- [ ] `make check` passes

## History

- 2026-11-26T11:27:21Z brisk-bronze-adder → planning
