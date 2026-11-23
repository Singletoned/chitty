---
title: Accept a `## Questions` task-list section in tickets
status: cold-read
parent: TASK-621
created: 2026-11-23
---

## Description

Part of TASK-621: an optional `## Questions` section. This ticket covers only the file format, reading it, and showing it. Adding and answering questions from the CLI and MCP is TASK-630; marking tickets in `chitty list` is TASK-631.

Format, decided while planning on 2026-11-23. It is the layout that both the pinned prettier (`--no-config`) and mdformat leave byte-identical; probes on 2026-11-23 showed that a lazy unindented answer line, and an answer on the line straight after its item, are both rewritten:

```markdown
## Questions

- [x] Which database?

  Postgres, because we already run it.

- [ ] Who owns the migration?
```

- Each item is `- [ ] text` or `- [x] text` (also `[X]`), parsed with the same line rules as Acceptance Criteria (`CRITERION_RE`). An indented line that comes directly after the item, with no blank line between, continues the question text and is joined with a space, as for criteria.
- An answer is one paragraph: indented lines that come after the item and one or more blank lines, before the next item or the end of the section. They are joined with a space. A second indented paragraph, or a nested list marker, raises `TaskError` (for example, `question 1: an answer must be one paragraph`). Any other line raises the same kind of error as in Acceptance Criteria, naming `## Questions`.
- The tick and the answer are independent when parsing: `[x]` with no answer and `[ ]` with an answer both parse. Rules for writing them belong to TASK-630.
- Rendering: `parse` keeps the original lines, so a file round-trips byte for byte. This ticket adds no way to write Questions apart from `with_section`. Nothing in this ticket renders new Question lines.

Code, in `src/chitty/model.py`:

- Add `"Questions"` to `SectionName` and a `QUESTIONS` constant. Put it in `SECTION_ORDER` straight after `ACCEPTANCE_CRITERIA`. The unknown-section error in `_split_sections` lists allowed names from that order, so it will include `Questions`, and any other `##` name stays refused.
- A frozen dataclass `Question(checked: bool, text: str, answer: str | None)` and `Task.questions: tuple[Question, ...]`, parsed in `parse` next to `_parse_criteria`, sharing code with it where that is simple.
- `with_section(QUESTIONS, text)` works as for other free sections. The result goes through `parse`, so an invalid Questions body is refused. Renumbering (`src/chitty/renumbering.py`) then rewrites ticket IDs in Questions with no change, because it already calls `with_section` for every section except History and Acceptance Criteria.
- `as_dict` adds `"questions": [{"index": n, "checked": ..., "text": ..., "answer": ...}]`, numbered from 1, as `acceptance_criteria` is. It is an empty list when there is no section.

`chitty show` (`_format` in `src/chitty/cli.py`) prints the section after Acceptance Criteria as `n. [x] text`. When there is an answer, it adds a line of three spaces followed by the answer. The section is left out when there are no questions.

Tests, in a new `tests/test_questions_section.py`:

- Parse: the example above gives two questions, `(True, "Which database?", "Postgres, because we already run it.")` and `(False, "Who owns the migration?", None)`. `render()` returns the text byte for byte.
- Continuation and wrapping: a question line followed directly by an indented line joins into the question text. An answer spread over two indented lines joins into one answer.
- Refusals: a second indented answer paragraph, an indented `- x` under an item, and an unindented non-item line each raise `TaskError` naming the section. A `## Questionz` heading still raises the unknown-section error.
- Formatters: in `tests/test_formatters.py`, give `sample()` the example section (through `with_section`), so the prettier and mdformat no-op tests cover it.
- `chitty show`: in a `RepoTestCase` repository, write a ticket file with the example section. `chitty show TASK-1` prints `## Questions`, `1. [x] Which database?`, `   Postgres, because we already run it.` and `2. [ ] Who owns the migration?` in that order. `show --json` has the two `questions` entries.
- Renumbering: a test next to the existing renumbering tests shows a ticket ID in a question rewritten.

Out of scope: CLI and MCP options (TASK-630), list markers (TASK-631), and Markdown warnings in `chitty check` for question text.

## Acceptance Criteria

- [ ] The parse, continuation, refusal, `chitty show` and renumbering tests in `tests/test_questions_section.py` pass, and fail before the change (the unknown-section case excepted). Record both runs in a note
- [ ] The prettier and mdformat tests in `tests/test_formatters.py` pass with the Questions section in `sample()`; `make check` passes

## History

- 2026-11-23T10:40:13Z witty-russet-gannet → backlog
- 2026-11-23T12:29:26Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T12:29:26Z witty-russet-gannet backlog → cold-read
