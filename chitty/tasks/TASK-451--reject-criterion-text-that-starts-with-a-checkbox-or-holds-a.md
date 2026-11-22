---
title: Reject criterion text that starts with a checkbox or holds a line break
status: review
labels:
  - bug
priority: medium
created: 2026-11-19
---

## Description

Criterion text is checked by `_criterion_text` in `src/chitty/model.py`, which `Task.with_criteria` calls for both `add` (`--ac`, `chitty add --ac`, MCP) and `set_criteria` (`--set-ac`, MCP). It rejects only empty text and text containing `\n`. Two bugs follow:

1. A leading checkbox is kept as text. On 2026-11-19 `chitty edit TASK-401 --set-ac 2 "[x] text"` stored `- [ ] [x] text`, and `chitty show` then printed `[ ] [x] text`. Once a ticket is in `review`, `--set-ac` is refused, so the doubled tick could not be removed.
2. Other line breaks change the text silently. `parse` splits the file with `str.splitlines`, which also breaks on `\r`, `\x0b`, `\x0c`, `\x1c`, `\x1d`, `\x1e`, `\x85`, `\u2028` and `\u2029`. A criterion containing one is stored, then read back as a criterion plus a continuation line, joined with a space. Found by a Hypothesis probe: `--set-ac 1` with `"a\x1d\tb"` reads back as `"a\x1d b"`.

Decisions:

- Reject, do not interpret. `_criterion_text` raises `TaskError` when the stripped text starts with `[ ]`, `[x]` or `[X]`, whatever follows it (so `[x]text` and `[x]` alone are refused), or with `-` followed by one or more spaces or tabs and then one of those boxes (so `- [ ] text` is refused too). The message is `acceptance criterion must not start with a checkbox ("<box>"); use --check or --uncheck to set the tick`, where `<box>` is the matched box as typed (`[ ]`, `[x]` or `[X]`). Tests assert that whole message.
- Extend the existing single-line check, which runs on the stripped text, to every character `str.splitlines` breaks on; so `a\x1d` (stripped to `a`) is accepted and `a\x1db` is refused, with the existing message `acceptance criterion must be a single line`.
- Out of scope: titles, labels and other fields (YAML-rendered, not affected), and existing ticket files that already hold a doubled tick.

Tests use Hypothesis, the repository's property-testing tool, in a new file `tests/test_property_criteria_text.py`, calling `Task.with_criteria` and `parse` directly (`new_task(title, created, description, criteria, fields)` builds a starting ticket). Text strategies must mix `st.text()` with values built from drawn text: a checkbox prefix (`[ ]`, `[x]`, `[X]`, each with and without `- `, with surrounding spaces) and one character from the `str.splitlines` set above inserted at a drawn position.

## Acceptance Criteria

- [ ] Round-trip property: starting criteria (one to four, some ticked) are drawn from printable text with no break character and no checkbox prefix. For any drawn text used as `add` or as `set_criteria` for a drawn index, `with_criteria` raises `TaskError` exactly when the stripped text is empty, starts with a checkbox prefix as defined in the Description, or holds a `str.splitlines` break character; otherwise `parse(task.render()).criteria` holds the edited criterion with text equal to the stripped input and unticked, and every other criterion with its text and tick unchanged. Fixed examples in the same file: `-[ ] x` and `a\x1d` are accepted, `-\t[x] x`, `[x]text` and `a\x1db` are refused. It fails on `main` (for example with `a\x1d\tb`).
- [ ] Rejection property: on a ticket with at least one criterion, for any drawn text whose stripped form starts with a checkbox prefix or holds a `str.splitlines` break character, both `add` and `set_criteria` raise `TaskError` with the message given in the Description. It fails on `main` for `[x] text`.
- [ ] CLI test in the same file, in a class inheriting `CliTestCase` from `tests/test_cli.py`: `run_cli("add", "T", "--ac", "one")` creates `TASK-1`; read the bytes of the file `run_cli("path", "TASK-1")` prints, run `edit TASK-1 --set-ac 1 '[x] text'` with `run_cli(..., exit_code=1)`, assert the output contains the whole checkbox message for `[x]`, and assert the file bytes are unchanged. It fails on `main`, where the edit exits 0.

## Notes

Suggestion origin: chitty

Planning issues found while inspecting the ticket and implementation:

- The description says `_criterion_text` rejects only newline and stores `a\x1d\tb`, but `src/chitty/model.py` already checks all `splitlines()` breaks using sentinels before stripping. Thus that example already raises `TaskError`, and criterion 1's stated main-branch failure example is wrong. Correct the root cause and choose an actual failing example (such as the required accepted `a\x1d`, currently rejected).
- Criterion 2 requires the specified message for any text with a checkbox prefix or an internal break, but an input such as `[x] a\nb` satisfies both conditions and the two required messages differ. Specify which error takes precedence and how the property asserts it.
- `_criterion_text` is also called by `Task.with_criterion_text`, not only `with_criteria`; existing `tests/test_property_criterion_text.py` exercises that method. Clarify whether the changed validation is intended there too, including its effect on existing callers.

Inspected `with_criteria`, `_criterion_text`, parser locations, existing property tests and the CLI fixture. The remaining implementation and regression verification were not run because the conflicting message requirement needs a planning decision first; the CLI criterion is independently specified.

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
