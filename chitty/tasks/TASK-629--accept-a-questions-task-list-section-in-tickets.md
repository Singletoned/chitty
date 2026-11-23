---
title: Accept a `## Questions` task-list section in tickets
status: error
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

- Each item is `- [ ] text` or `- [x] text` (also `[X]`), parsed with the same line rules as Acceptance Criteria (`CRITERION_RE`). A line is indented when its first character is a space or tab (`line[0] in " \t"`, as for criteria). An indented line that comes directly after the item, with no blank line between, continues the question text and is joined with a space, as for criteria.
- An answer is one paragraph: indented lines that come after the item and one or more blank lines, before the next item or the end of the section. They are joined with a space. A second indented paragraph (indented lines after the answer and a blank line), or a nested list marker, raises `TaskError`, with the messages given under Code. Any other line raises the same kind of error as in Acceptance Criteria, naming `## Questions`.
- The tick and the answer are independent when parsing: `[x]` with no answer and `[ ]` with an answer both parse. Rules for writing them belong to TASK-630.
- Rendering: `parse` keeps the original lines, so a file round-trips byte for byte. This ticket adds no way to write Questions apart from `with_section`. Nothing in this ticket renders new Question lines.

Code, in `src/chitty/model.py`:

- Add `"Questions"` to `SectionName` and a `QUESTIONS` constant. Put it in `SECTION_ORDER` straight after `ACCEPTANCE_CRITERIA`. The unknown-section error in `_split_sections` lists allowed names from that order, so it will include `Questions`, and any other `##` name stays refused.
- A frozen dataclass `Question(checked: bool, text: str, answer: str | None)` and `Task.questions: tuple[Question, ...]`, parsed in `parse` by a new `_parse_questions`, next to `_parse_criteria`, which it does not share code with. The rules differ: criteria skip blank lines and join any later indented line, while Questions treat indented lines after a blank line as the answer. Its errors name the section: an empty item `- [ ]` raises `question <n> has no text`; a nested list marker raises `question <n>: nested lists are not allowed`; a second answer paragraph raises `question <n>: an answer must be one paragraph`; any other line raises `'## Questions' may only contain '- [ ] ...' items; found <line repr>`. A whitespace-only line counts as blank everywhere in the section. A nested list marker is a stripped line matching `LIST_MARKER_RE`, as for criteria. Blank lines between items and at the end of the section are allowed, and an unanswered question may be followed by a blank line and then the next item.
- `with_section(QUESTIONS, text)` works as for other free sections. The result goes through `parse`, so an invalid Questions body is refused. Renumbering (`src/chitty/renumbering.py`) then rewrites ticket IDs in Questions with no change, because it already calls `with_section` for every section except History and Acceptance Criteria.
- `as_dict` adds `"questions": [{"index": n, "checked": ..., "text": ..., "answer": ...}]`, numbered from 1, as `acceptance_criteria` is; `answer` is `null` when there is none. It is an empty list when there is no section.

`chitty show` (`_format` in `src/chitty/cli.py`, which today special-cases only Acceptance Criteria; add a Questions branch rather than printing the raw section) prints the section after Acceptance Criteria as `n. [x] text`. When there is an answer, it adds a line of three spaces followed by the answer. The section is left out when there are no questions.

Tests, in a new `tests/test_questions_section.py`:

- Parse: the example above gives two questions, `(True, "Which database?", "Postgres, because we already run it.")` and `(False, "Who owns the migration?", None)`. `render()` returns the text byte for byte.
- Ticks: `- [X] Q` parses as checked.
- Continuation and wrapping: a question line followed directly by an indented line joins into the question text. An answer spread over two indented lines joins into one answer.
- Refusals: `- [ ]` with no text, a second indented answer paragraph, an indented `- x` under an item, and an unindented non-item line each raise `TaskError` with the exact message given under Code.
- Property, with Hypothesis and `examples(50)` from `tests/__init__.py`: build Questions bodies from one to five items, each with a drawn tick (` `, `x`, `X`), text of one to three words of `string.ascii_letters` joined by single spaces (so no leading or trailing space), an optional continuation line, and an optional answer: one or two indented lines with no blank line between them, after the item (or its continuation line) and one or two blank lines. Items are separated by one or two blank lines. Each indented line draws its indent from two spaces, four spaces and a tab. Then `parse` succeeds, `render()` is byte-identical, and `as_dict()["questions"]` has one entry per item, with the drawn tick, text and answer (text and answer as their lines joined with single spaces). A `## Questionz` heading still raises the unknown-section error, whose list of allowed names now includes `Questions`.
- Formatters: in `tests/test_formatters.py`, give `sample()` the example section (through `with_section`), so the prettier and mdformat no-op tests cover it.
- `chitty show`: in a `RepoTestCase` repository, write a ticket file with the example section. `chitty show TASK-1` prints `## Questions`, `1. [x] Which database?`, `   Postgres, because we already run it.` and `2. [ ] Who owns the migration?` in that order. `show --json` has the two `questions` entries.
- Renumbering, in `tests/test_questions_section.py` (not next to the other renumbering tests, so all of this ticket's tests are in one file): `parse` a minimal valid ticket text, `"---\ntitle: T\nstatus: todo\ncreated: 2026-11-23\n---\n\n## Description\n\nD.\n\n## Acceptance Criteria\n\n- [ ] A\n"` (which round-trips on `main`) followed by `"\n## Questions\n\n"` and the body, whose Questions section is `- [ ] Does TASK-7 block TASK-70?` then a blank line then `  Yes, see TASK-7.`; call `chitty.renumbering.rewrite_task(task, {TaskId("TASK", 7): TaskId("TASK", 12)})`. Assert the result's `questions` is `(Question(False, "Does TASK-12 block TASK-70?", "Yes, see TASK-12."),)` (so `TASK-70` is untouched) and its `section(QUESTIONS)` is the original body with both `TASK-7` replaced by `TASK-12`. Before the change it fails because `parse` refuses `## Questions`.

Out of scope: CLI and MCP options (TASK-630), list markers (TASK-631), and Markdown warnings in `chitty check` for question text.

## Acceptance Criteria

- [ ] The tick, parse, continuation, refusal, property, `chitty show` and renumbering tests in `tests/test_questions_section.py` pass, and each fails before the change. Record each test's failure message in a note, so a reviewer can see which failed on its own assertion and which only because `## Questions` was refused
- [ ] The prettier and mdformat tests in `tests/test_formatters.py` pass with the Questions section in `sample()`; `make check` passes

## Plan

Add focused parsing, rendering, CLI, formatter, and renumbering tests; record their pre-fix failures. Implement Questions parsing and presentation, run formatting and make check, then commit and request review.

## Notes

Planner, 2026-11-23: the test placement contradiction is resolved: every test, renumbering included, is in `tests/test_questions_section.py`, and the renumbering test now has its fixture, call and assertions. Earlier cold reads (two) found nothing else outstanding.

Runner error (agent): TASK-629 is still `doing` after 5 continuations with no new work committed; only committed changes are visible to `chitty run`

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-629`

Error output:

```text
last session: exit 0 after 9s
I have not completed TASK-629 or changed its status. No implementation files were changed. I cannot substantiate a ticket defect or external blocker, so I have not moved it to `planning` or `blocked`.
```

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
