---
title: Split ticket files only at \n, so criteria can hold other Unicode line separators
status: cold-read
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
- Out of scope: the History parsing in `transitions` and `timed_transitions`, which uses `str.splitlines` on History text that Chitty writes itself; frontmatter (YAML); and `src/chitty/check.py`, which already splits on `\n`. A frontmatter value holding one of these characters is also out of scope, and no test covers it.

Tests go in a new file, `tests/test_criteria_line_breaks.py`:

- Property, with Hypothesis and `examples(50)` from `tests/__init__.py`. Draw a ticket with criteria using `ticket_texts([TaskId("TASK", 1)])` from `tests/ticket_strategies.py`, filtered as `tests/test_property_criterion_text.py` does. Draw an index and a text: `st.text()` with `\n` and `\r` excluded, mixed through `st.one_of` with drawn text that has one of the other `splitlines` characters above inserted at a drawn position, and filtered so the stripped text is non-empty. Build `parse(task.with_criteria(add=[], remove=[], set_criteria=[(index, text)], check=[], uncheck=[]).render())`. Assert that criterion `index` has text equal to `text.strip()` and is unticked, and that every other criterion keeps its text and its tick. Assert the same for `add=[text]`, where the appended last criterion has that text.
- Examples: for each break character in the list above other than `\n` and `\r`, `set_criteria` with `f"a{c}b"` round-trips as that exact text; `f"a{c}"` round-trips as `a`; `a\nb` and `a\rb` each raise `TaskError` with the message `acceptance criterion must be a single line`; `a\n` is stored as `a`; `[x] a` round-trips as the text `[x] a`, unticked.
- Parse example: a ticket file whose Acceptance Criteria section holds `- [ ] a\u2028b\n` parses to one criterion with text `a\u2028b`, and `render` returns the input byte for byte.
- CLI test, in a class that inherits `CliTestCase` from `tests/test_cli.py`: `run_cli("add", "T", "--ac", "one")`, then `run_cli("edit", "TASK-1", "--set-ac", "1", "a\u2028b")` exits 0, and `show TASK-1 --json` gives criterion text `a\u2028b`.

Run every test against `main` before the change and record the failures in a note. The property, the examples using inner characters, the parse example and the CLI test all fail there. The `\n` refusal passes on both.

## Acceptance Criteria

- [ ] The property, the break-character examples, the parse example and the CLI test in `tests/test_criteria_line_breaks.py` pass. Against `main`, each fails except three that already pass there: the `a\nb` and `a\rb` refusals and the `[x] a` example. Record both runs in a note
- [ ] `tests/test_property_criterion_text.py` and the other existing tests still pass; `make check` passes
- [ ] `with_criterion_text`, used by `src/chitty/renumbering.py`, follows the same rule; `tests/test_property_renumbering.py` passes

## Notes

Suggestion origin: chitty

Planning issues found while inspecting the ticket and implementation:

- The description says `_criterion_text` rejects only newline and stores `a\x1d\tb`, but `src/chitty/model.py` already checks all `splitlines()` breaks using sentinels before stripping. Thus that example already raises `TaskError`, and criterion 1's stated main-branch failure example is wrong. Correct the root cause and choose an actual failing example (such as the required accepted `a\x1d`, currently rejected).
- Criterion 2 requires the specified message for any text with a checkbox prefix or an internal break, but an input such as `[x] a\nb` satisfies both conditions and the two required messages differ. Specify which error takes precedence and how the property asserts it.
- `_criterion_text` is also called by `Task.with_criterion_text`, not only `with_criteria`; existing `tests/test_property_criterion_text.py` exercises that method. Clarify whether the changed validation is intended there too, including its effect on existing callers.

Inspected `with_criteria`, `_criterion_text`, parser locations, existing property tests and the CLI fixture. The remaining implementation and regression verification were not run because the conflicting message requirement needs a planning decision first; the CLI criterion is independently specified.

Review failed (design): The previous planning note remains unresolved; this branch contains only ticket edits and no implementation or test file. Correct the existing validation claim and regression example, and decide error precedence for inputs matching both rejection rules before work resumes. The previous note also identifies the shared `with_criterion_text` caller; clarify its intended coverage and effects. No Decided note or focused test exists.
1: fail - The prior planning note remains unresolved: `_criterion_text` checks splitlines before stripping, contrary to the description and claimed `a\x1d\tb` baseline failure. The required property test and implementation are absent, so regression and round-trip verification were not possible. Specify a genuine baseline failure.
2: fail - The prior planning note remains unresolved: `[x] a\nb` requires two different messages under the current wording. Specify precedence and the property assertion; the required test is absent.
3: fail - The independently specified CLI test is absent from `tests/test_property_criteria_text.py`; no change exists to verify against main. Add the specified regression test and implementation after planning.

Planner, 2026-11-23: rewritten. The earlier notes are resolved: the splitlines check that already exists is now described correctly; the checkbox rejection is dropped, so there is no question of which error takes precedence; and `with_criterion_text` shares `_criterion_text`, so it gets the same rule, which existing tests cover. TASK-638 has been folded into this ticket.

Planner, 2026-11-23, after the first cold read: `\r` is still refused, because otherwise a criterion could make its ticket file unreadable. Code points are written as escapes, not raw characters. Frontmatter is out of scope. The test file is renamed, so it is not confused with `tests/test_property_criterion_text.py`. The `with_criteria` docstring is to be updated.

Planner, 2026-11-23, after the second cold read: corrected what `parse` does today with an unindented break, added an example pinning the checkbox-text decision, and named the renumbering caller. Nothing serious was found.

Planning blocker: criterion 1 requires all new tests except the newline and carriage-return refusals to fail against main, but the description explicitly requires `[x] a` to remain accepted as today. The current `_criterion_text` and parser already round-trip that text unticked; verified locally with `parse` and `with_criteria`, yielding `Criterion(checked=False, text='[x] a', ...)`. The required checkbox example therefore cannot both pass after the change and fail before it. Correct criterion 1 to exclude this existing-behaviour example from the baseline-failure requirement (and specify baseline expectations per example if tests are grouped).

Inspected `parse`, `with_criteria`, `with_criterion_text`, the existing criterion and renumbering property tests, and the CLI fixture. The remaining requested tests and `make check` were not run: the new test file does not exist and implementation is stopped pending correction. The newline/carriage-return validation and shared caller can be independently located, but the complete baseline and post-change verification cannot be established until the contradiction is resolved.

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
