---
title: Reject criterion text that starts with a checkbox or holds a line break
status: planning
labels:
  - bug
priority: medium
created: 2026-11-19
---

## Description

Criterion text is checked by `_criterion_text` in `src/chitty/model.py`, which `Task.with_criteria` calls for both `add` (`--ac`, `chitty add --ac`, MCP) and `set_criteria` (`--set-ac`, MCP). It rejects only empty text and text containing `\n`. Two bugs follow:

1. A leading checkbox is kept as text. On 2026-11-19 `chitty edit TASK-401 --set-ac 2 "[x] text"` stored `- [ ] [x] text`, and `chitty show` then printed `[ ] [x] text`. Once a ticket is in `review`, `--set-ac` is refused, so the doubled tick could not be removed.
2. Other line breaks change the text silently. `parse` splits the file with `str.splitlines`, which also breaks on `\r`, `\x0b`, `\x0c`, `\x1c`, `\x1d`, `\x1e`, `\x85`, ` ` and ` `. A criterion containing one is stored, then read back as a criterion plus a continuation line, joined with a space. Found by a Hypothesis probe: `--set-ac 1` with `"a\x1d\tb"` reads back as `"a\x1d b"`.

Decisions:

- Reject, do not interpret. `_criterion_text` raises `TaskError` when the stripped text starts with `[ ]`, `[x]` or `[X]`, alone or after a `- ` list marker (so `- [ ] text` is refused too). The message says the tick belongs in `--check`/`--uncheck`, for example `acceptance criterion must not start with a checkbox ("[x]"); use --check or --uncheck to set the tick`.
- Extend the existing single-line check to every character `str.splitlines` breaks on, with the existing message `acceptance criterion must be a single line`.
- Out of scope: titles, labels and other fields (YAML-rendered, not affected), and existing ticket files that already hold a doubled tick.

Tests use Hypothesis, the repository's property-testing tool, in a new file `tests/test_property_criteria_text.py`, calling `Task.with_criteria` and `parse` directly (`new_task(title, created, description, criteria, fields)` builds a starting ticket). Text strategies must mix `st.text()` with values built from drawn text: a checkbox prefix (`[ ]`, `[x]`, `[X]`, each with and without `- `, with surrounding spaces) and one character from the `str.splitlines` set above inserted at a drawn position.

## Acceptance Criteria

- [ ] Round-trip property: for a ticket with one to four drawn criteria, some ticked, and any drawn text used as `add` or as `set_criteria` for a drawn index, `with_criteria` either raises `TaskError`, or `parse(task.render()).criteria` holds the edited criterion with text equal to the stripped input and unticked, and every other criterion with its text and tick unchanged. It fails on `main` (for example with `a\x1d\tb`).
- [ ] Rejection property: for any drawn text that, stripped, starts with a checkbox prefix or that holds any `str.splitlines` break character, both `add` and `set_criteria` raise `TaskError` with the message given in the Description. It fails on `main` for `[x] text`.
- [ ] In a temporary repository, `chitty edit <ID> --set-ac 1 '[x] text'` exits non-zero, prints the checkbox message, and leaves the ticket file byte-identical (a test in the same new file, using the existing CLI test helpers).

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:25Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:27Z sunny-white-dormouse: changed notes
- 2026-11-19T21:00:22Z sunny-white-dormouse: changed title, labels, priority, description, acceptance criteria
- 2026-11-19T21:00:22Z sunny-white-dormouse backlog → planning
