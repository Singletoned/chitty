---
title: Parse a `## Questions` task-list section in tickets
status: doing
parent: TASK-621
created: 2026-11-23
---

## Description

Part of TASK-621: an optional `## Questions` section. This ticket only lets `parse` in `src/chitty/model.py` read question items. Answers are TASK-10035; `as_dict` is TASK-649; `chitty show` is TASK-650.

The full format (answers come in TASK-10035):

```markdown
## Questions

- [x] Which database?

  Postgres, because we already run it.

- [ ] Who owns the migration?
```

Code, in `src/chitty/model.py`:

- Add `"Questions"` to `SectionName`, a `QUESTIONS` constant, and put it in `SECTION_ORDER` straight after `ACCEPTANCE_CRITERIA`.
- A frozen dataclass `Question(checked: bool, text: str, answer: str | None)` and `Task.questions: tuple[Question, ...]`, filled by a new `_parse_questions` next to `_parse_criteria`. In this ticket `answer` is always `None`.
- Items are `- [ ] text`, `- [x] text` or `- [X] text`, matched with `CRITERION_RE`. An indented line (first character a space or tab) directly after an item, with no blank line between, continues its text, joined with a space. Blank (or whitespace-only) lines between items and at the end are allowed.
- Errors (`TaskError`), with these exact messages and, like criteria, no `line N:` prefix: `- [ ]` with no text gives `question <n> has no text`; an indented line whose stripped text matches `LIST_MARKER_RE` gives `question <n>: nested lists are not allowed`; any other line gives `'## Questions' may only contain '- [ ] ...' items; found <stripped line repr>` (as `_parse_criteria` formats it). Unlike criteria, an indented line after a blank line is one of these other lines: TASK-10035 makes it an answer.
- `SECTION_ORDER` is also looped over by `_format` in `src/chitty/cli.py`, `src/chitty/renumbering.py` and `src/chitty/import_backlog.py`; Questions passes through them unchanged (raw in `chitty show` until TASK-650, IDs rewritten by renumbering), which is intended. Update the refusal list in the `parse()` docstring.
- `parse` keeps the original lines, so `render()` is byte-identical, as for other sections.

Tests, in a new `tests/test_questions_section.py` (each fails today because `parse` refuses `## Questions`):

- Two items, `- [x] Which database?` and `- [ ] Who owns the migration?` separated by a blank line, give `(Question(True, "Which database?", None), Question(False, "Who owns the migration?", None))`, and `render()` returns the text unchanged. `- [X] Q` parses as checked.
- `- [ ] Q\n  more\n` gives text `"Q more"`.
- The three refusals above, each checked with `assertEqual(str(error), ...)` on the exact message, including an indented line after a blank.
- A `## Questionz` heading is still refused, and the error's list of allowed names includes `Questions`.

Out of scope: answers (TASK-10035), the formatter tests, renumbering, `as_dict`, `chitty show`, and CLI or MCP options.

## Acceptance Criteria

- [ ] The parse, continuation, refusal and unknown-section tests in `tests/test_questions_section.py` pass, and each fails before the change; record the failure messages in a note
- [ ] `make check` passes

## Plan

Add focused failing parser tests, then introduce the Questions section and immutable question model with strict continuation and error handling. Run formatting and checks, commit, and hand off for review.

## Notes

Split 2026-11-26 after four stalled worker runs: answers, the formatter sample and the renumbering test moved to TASK-10035.

Before implementation, all seven tests in `tests/test_questions_section.py` failed: the item, uppercase and continuation tests raised `line 11: unknown section 'Questions'`; the three refusal tests received that same error instead of their expected exact messages; the unknown-section test found `Questions` missing from the allowed names.

## History

- 2026-11-23T10:40:13Z witty-russet-gannet → backlog
- 2026-11-23T12:29:26Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T12:29:26Z witty-russet-gannet backlog → cold-read
- 2026-11-23T12:30:30Z witty-russet-gannet: changed description, acceptance criteria, notes
- 2026-11-23T12:31:36Z witty-russet-gannet: changed description, acceptance criteria, notes
- 2026-11-23T12:31:36Z witty-russet-gannet cold-read → todo
- 2026-11-23T13:02:02Z friendly-yellow-ibis todo → doing
- 2026-11-23T13:05:23Z friendly-yellow-ibis: wrote the plan
- 2026-11-23T13:05:35Z friendly-yellow-ibis: changed notes
- 2026-11-23T13:06:22Z friendly-yellow-ibis: changed notes
- 2026-11-23T13:06:28Z friendly-yellow-ibis: changed owner, notes
- 2026-11-23T13:06:28Z friendly-yellow-ibis doing → planning
- 2026-11-23T18:45:57Z witty-yellow-vole: replaced notes; changed owner, description
- 2026-11-23T18:46:04Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:46:16Z witty-yellow-vole: changed description
- 2026-11-23T18:46:16Z witty-yellow-vole cold-read → planning
- 2026-11-23T18:46:18Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:47:41Z witty-yellow-vole: changed description
- 2026-11-23T18:47:41Z witty-yellow-vole cold-read → planning
- 2026-11-23T18:47:53Z witty-yellow-vole: changed description
- 2026-11-23T18:47:58Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:48:23Z witty-yellow-vole cold-read → planning
- 2026-11-23T18:48:27Z witty-yellow-vole planning → todo
- 2026-11-23T19:01:30Z tidy-teal-adder todo → doing
- 2026-11-23T19:06:15Z tidy-teal-adder: changed notes
- 2026-11-23T19:06:15Z tidy-teal-adder doing → error
- 2026-11-23T19:43:38Z friendly-coral-badger: changed title, description, acceptance criteria, notes; wrote the plan
- 2026-11-23T19:43:38Z friendly-coral-badger error → planning
- 2026-11-23T19:43:50Z friendly-coral-badger planning → cold-read
- 2026-11-23T19:45:36Z friendly-coral-badger: changed description
- 2026-11-23T19:45:36Z friendly-coral-badger cold-read → planning
- 2026-11-23T19:45:48Z friendly-coral-badger: changed description, notes
- 2026-11-23T19:45:55Z friendly-coral-badger planning → todo
- 2026-11-23T20:00:46Z honest-bronze-dormouse todo → doing
- 2026-11-23T20:03:27Z honest-bronze-dormouse: wrote the plan
- 2026-11-23T20:04:34Z honest-bronze-dormouse: changed notes
- 2026-11-23T20:04:34Z honest-bronze-dormouse doing → error
- 2026-11-23T21:11:41Z friendly-coral-badger: changed notes
- 2026-11-23T21:11:41Z friendly-coral-badger error → todo
- 2026-11-23T21:29:50Z zesty-hazel-dormouse todo → doing
- 2026-11-23T21:33:26Z zesty-hazel-dormouse: wrote the plan
- 2026-11-23T21:33:52Z zesty-hazel-dormouse: changed owner, notes
- 2026-11-23T21:33:52Z zesty-hazel-dormouse doing → planning
- 2026-11-24T08:46:26Z sunny-hazel-gannet: changed owner, notes
- 2026-11-24T08:46:26Z sunny-hazel-gannet planning → todo
- 2026-11-24T09:22:57Z sunny-khaki-crane todo → doing
- 2026-11-24T09:25:19Z sunny-khaki-crane: wrote the plan
- 2026-11-24T09:25:59Z sunny-khaki-crane: changed owner, notes
- 2026-11-24T09:25:59Z sunny-khaki-crane doing → planning
- 2026-11-26T11:28:10Z brisk-bronze-adder: changed notes
- 2026-11-26T11:28:10Z brisk-bronze-adder planning → to-plan
- 2026-11-26T11:28:19Z brisk-bronze-adder to-plan → planning
- 2026-11-26T11:28:26Z brisk-bronze-adder: replaced notes; changed description, acceptance criteria; wrote the plan
- 2026-11-26T11:28:26Z brisk-bronze-adder planning → cold-read
- 2026-11-26T11:30:27Z brisk-bronze-adder: changed description
- 2026-11-26T11:30:27Z brisk-bronze-adder cold-read → planning
- 2026-11-26T11:30:33Z brisk-bronze-adder: changed owner
- 2026-11-26T11:30:33Z brisk-bronze-adder planning → todo
- 2026-11-26T13:03:07Z lively-dusky-quail todo → doing
- 2026-11-26T13:07:03Z lively-dusky-quail: wrote the plan
- 2026-11-26T13:07:31Z lively-dusky-quail: changed notes
