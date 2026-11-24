---
title: Split ticket files only at \n, so criteria can hold other Unicode line separators
status: planning
labels:
  - bug
priority: medium
created: 2026-11-19
---

## Description

A criterion is refused when it holds a character that only Python treats as a line break. On 2026-11-23, `chitty edit TASK-610 --set-ac 1 ...` was refused with `acceptance criterion must be a single line` because the text held U+2028 LINE SEPARATOR; finding it took guesswork (TASK-638).

Cause, in `src/chitty/model.py`:

- `parse` splits the file with `text.splitlines(keepends=True)`. `str.splitlines` breaks on `\n`, `\r`, `\x0b`, `\x0c`, `\x1c`, `\x1d`, `\x1e`, `\x85`, `\u2028` and `\u2029`. Markdown (CommonMark) ends lines only at `\n` and `\r`, and `parse` already refuses `\r`. So a criterion `- [ ] a\u2028b` is refused by `parse` with `may only contain '- [ ] ...' items`, because the text after the break is not indented; an indented one is read as a continuation line and joined with a space.
- To avoid that, `_criterion_text` refuses any text in which `splitlines` finds a break, including at either end (it adds a sentinel character to each end before splitting), before it strips the text.

Decisions:

- Make the parser accept these characters, rather than refusing them in the criterion text. In `parse`, split lines only at `\n`, keeping the line endings, and leave the rest of `parse` unchanged. Other sections already round-trip byte for byte, because `render` joins the lines back together.
- In `_criterion_text`, strip the text first, then refuse it only if the stripped text still contains `\n` or `\r` (`parse` refuses any `\r` in a file, so a stored `\r` would make the ticket unreadable). The message stays `acceptance criterion must be a single line`. Update the `with_criteria` docstring, which says replacement text must contain no line breaks even at the ends. As a result, `a\u2028b` and `a\x1db` are stored as given, and `a\n` and `a\u2028` are stored as `a`, because `str.strip` removes surrounding whitespace, and Python counts these characters as whitespace.
- Decided 2026-11-23, following the person's standing rule (make tools robust to unusual input, such as a criterion that looks like a checkbox): text that starts with `[x]` or `[ ]` is stored as text, as it is today. Nothing in this ticket refuses it. That reverses the checkbox rejection in this ticket's earlier version.
- Frontmatter: after the change, `parse` no longer splits frontmatter at `\x85`, and PyYAML folds a raw `\x85` inside a scalar into a space, so a title `a\x85b` would silently be read back as `a b` (checked on a trial patch, 2026-11-24). Today such a title makes the file unreadable. Fix it in `render_scalar`: before its other quoting rules, if the value contains `\x85`, return `json.dumps(value, ensure_ascii=False).replace("\x85", "\\u0085")`, a double-quoted YAML scalar whose `\u0085` escape reads back as the character. `\u2028` and `\u2029` already read back unchanged after the change, so they need nothing.
- Headings: a line such as `x\u2028## Plan` in a section is one line after the change, so its `## Plan` is not a heading. That matches CommonMark and is intended.
- Out of scope: the History parsing in `transitions` and `timed_transitions`, which uses `str.splitlines` on History text that Chitty writes itself; `_text_lines`, which right-strips section lines; and `src/chitty/check.py`, which already splits on `\n`.

Tests go in a new file, `tests/test_criteria_line_breaks.py`:

- Property, with Hypothesis and `examples(50)` from `tests/__init__.py`. Draw a ticket with criteria using `ticket_texts([TaskId("TASK", 1)])` from `tests/ticket_strategies.py`, filtered as `tests/test_property_criterion_text.py` does. Draw an index and a text: `st.text()` with `\n` and `\r` excluded, mixed through `st.one_of` with drawn text that has one of the other `splitlines` characters above inserted at a drawn position, and filtered so the stripped text is non-empty. Build `parse(task.with_criteria(add=[], remove=[], set_criteria=[(index, text)], check=[], uncheck=[]).render())`. Assert that criterion `index` has text equal to `text.strip()` and is unticked, and that every other criterion keeps its text and its tick. Assert the same for `add=[text]`, where the appended last criterion has that text.
- Existing test: `test_new_criterion_rejects_all_line_breaks` in `tests/test_model.py` asserts that every `splitlines` character is refused; narrow it to `\n` and `\r` (the trial patch showed it is the only existing test the change breaks). `tests/test_cli.py` refusing a suggestion titled `\u2028` is unaffected: `_check_single_line` refuses it as empty after stripping.
- Examples: for each break character in the list above other than `\n` and `\r`, `set_criteria` with `f"a{c}b"` round-trips as that exact text; `f"a{c}"` round-trips as `a`; `a\nb` and `a\rb` each raise `TaskError` with the message `acceptance criterion must be a single line`; `a\n` is stored as `a`; `[x] a` round-trips as the text `[x] a`, unticked.
- Parse example: a ticket file whose Acceptance Criteria section holds `- [ ] a\u2028b\n` parses to one criterion with text `a\u2028b`, and `render` returns the input byte for byte.
- Renumbering-caller example, in the same new file: for `text` in `a\u2028b` and `a\x1db`, `parse(parse(SAMPLE).with_criterion_text(1, text).render()).criteria[0].text == text`, with `SAMPLE` imported from `tests/test_model.py`.
- Frontmatter example, with `subTest` for each of `\x85`, `\u2028` and `\u2029` as `c`: `parse(task.with_field("title", f"a{c}b").render()).frontmatter.title == f"a{c}b"`, where `task = parse(SAMPLE)`. For `\x85`, the rendered title line is also `title: "a\u0085b"`, with the six characters backslash, `u`, `0`, `0`, `8`, `5` between the quotes, not the raw character. All three fail on `main`, where the file cannot be read back.
- CLI test, in a class that inherits `CliTestCase` from `tests/test_cli.py`: `run_cli("add", "T", "--ac", "one")`, then `run_cli("edit", "TASK-1", "--set-ac", "1", "a\u2028b")` exits 0, and `show TASK-1 --json` gives criterion text `a\u2028b`.

Put the `a\nb` and `a\rb` refusals and the `[x] a` example in a class `TestUnchangedBehaviour`, and every other new test in a class `TestBreaksAccepted`. Write each kind of example as its own test method, using `subTest` for each character, so a run shows which kinds pass. Run every test against `main` before the change and record the results in a note. Expected on `main`: the property, the parse example, the renumbering-caller example, the frontmatter example, the CLI test and the `a{c}b`, `a{c}` and `a\n` examples fail; the `a\nb` and `a\rb` refusals and the `[x] a` example pass, because they pin behaviour this ticket keeps. After the change, all pass.

## Acceptance Criteria

- [ ] The tests in `tests/test_criteria_line_breaks.py` pass. A note records a run of that file against `main`: every test in `TestBreaksAccepted` fails there, and every test in `TestUnchangedBehaviour` passes there, because those pin behaviour this ticket keeps; `test_new_criterion_rejects_all_line_breaks` is narrowed to `\n` and `\r`
- [ ] `tests/test_property_criterion_text.py` and the other existing tests still pass; `make check` passes
- [ ] The renumbering-caller example (`with_criterion_text` with `a\u2028b` and `a\x1db`) passes and fails against `main`; `tests/test_property_renumbering.py` passes
- [ ] The frontmatter example passes (a title `a\x85b` reads back unchanged, written as `"a\u0085b"`) and fails against `main`

## Plan

Implement the agreed ticket: first run the specified new regression cases against main and record baseline results; add focused tests, update parser line splitting and criterion validation, and preserve YAML round-tripping for NEL. Run targeted tests and make check, then commit implementation and tests and hand off to review.

## Notes

Suggestion origin: chitty

Planner, 2026-11-24: current state. Every earlier planning blocker is resolved, and the notes that raised them were removed to stop them being re-raised (they are in Git history). In particular, `[x] a` and the `\n`/`\r` refusals are expected to pass on `main`: they are in `TestUnchangedBehaviour`, and criterion 1 asks only `TestBreaksAccepted` to fail there. Two cold reads on 2026-11-24 found nothing serious, and a trial patch of the planned change, run against the whole suite, broke only `test_new_criterion_rejects_all_line_breaks`.

## History

- 2026-11-19T20:55:25Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:27Z sunny-white-dormouse: changed notes
- 2026-11-19T21:00:22Z sunny-white-dormouse: changed title, labels, priority, description, acceptance criteria
- 2026-11-19T21:00:22Z sunny-white-dormouse backlog → planning
- 2026-11-19T21:01:24Z sunny-white-dormouse: changed acceptance criteria
- 2026-11-19T21:01:24Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:03:38Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:03:38Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:03:49Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:05:29Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:05:29Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:05:47Z sunny-white-dormouse planning → todo
- 2026-11-20T00:41:45Z nimble-fawn-eel todo → doing
- 2026-11-22T21:26:06Z rosy-pearl-falcon: changed owner, notes
- 2026-11-22T21:26:06Z rosy-pearl-falcon doing → planning
- 2026-11-22T22:01:15Z human planning → review
- 2026-11-22T22:04:08Z witty-ebony-puffin: changed owner, acceptance criteria, notes
- 2026-11-22T22:04:08Z witty-ebony-puffin review → planning
- 2026-11-23T12:02:04Z witty-russet-gannet: changed title, description, acceptance criteria, notes
- 2026-11-23T12:02:04Z witty-russet-gannet planning → cold-read
- 2026-11-23T12:04:56Z witty-russet-gannet: changed description, acceptance criteria, notes
- 2026-11-23T12:06:43Z witty-russet-gannet: changed description, acceptance criteria, notes
- 2026-11-23T12:06:43Z witty-russet-gannet cold-read → todo
- 2026-11-23T12:34:57Z plucky-jade-dormouse todo → doing
- 2026-11-23T12:38:43Z plucky-jade-dormouse: changed owner, notes
- 2026-11-23T12:38:43Z plucky-jade-dormouse doing → planning
- 2026-11-23T23:05:38Z mellow-amber-toad: changed acceptance criteria
- 2026-11-23T23:05:38Z mellow-amber-toad planning → cold-read
- 2026-11-23T23:07:50Z mellow-amber-toad: changed description
- 2026-11-23T23:07:50Z mellow-amber-toad cold-read → planning
- 2026-11-23T23:07:56Z mellow-amber-toad planning → todo
- 2026-11-23T23:25:25Z mellow-amber-urchin todo → doing
- 2026-11-23T23:27:54Z mellow-amber-urchin: changed owner, notes
- 2026-11-23T23:27:54Z mellow-amber-urchin doing → planning
- 2026-11-24T07:33:08Z sunny-hazel-gannet: changed description, acceptance criteria
- 2026-11-24T07:33:08Z sunny-hazel-gannet planning → cold-read
- 2026-11-24T07:41:10Z sunny-hazel-gannet: changed description, acceptance criteria
- 2026-11-24T07:43:37Z sunny-hazel-gannet: changed description
- 2026-11-24T07:43:37Z sunny-hazel-gannet cold-read → planning
- 2026-11-24T07:43:39Z sunny-hazel-gannet planning → todo
- 2026-11-24T07:44:08Z sunny-hazel-gannet: changed description
- 2026-11-24T09:18:36Z kind-teal-urchin todo → doing
- 2026-11-24T09:21:07Z kind-teal-urchin: wrote the plan
- 2026-11-24T09:21:21Z kind-teal-urchin: changed owner, notes
- 2026-11-24T09:21:21Z kind-teal-urchin doing → planning
- 2026-11-24T09:27:09Z sunny-hazel-gannet: replaced notes; changed owner, description, acceptance criteria
