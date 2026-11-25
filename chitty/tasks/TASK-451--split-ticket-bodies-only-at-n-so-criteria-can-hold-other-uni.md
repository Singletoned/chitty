---
title: Split ticket bodies only at `\n`, so criteria can hold other Unicode line separators
status: review
labels:
  - bug
priority: medium
created: 2026-11-19
---

## Description

A criterion is refused when it holds a character that only Python treats as a line break. On 2026-11-23, `chitty edit TASK-610 --set-ac 1 ...` was refused with `acceptance criterion must be a single line` because the text held U+2028 LINE SEPARATOR.

Cause, in `src/chitty/model.py`: `parse` splits the whole file with `text.splitlines(keepends=True)`, which also breaks on `\x0b`, `\x0c`, `\x1c`, `\x1d`, `\x1e`, `\x85`, `\u2028` and `\u2029`. Markdown ends lines only at `\n` (and `parse` already refuses `\r`). `_criterion_text` refuses any text in which `splitlines` finds a break, to stay consistent with `parse`.

Change, in `src/chitty/model.py` only:

- `parse`: keep finding the frontmatter exactly as today, but split the body (everything after the closing `---`) only at `\n`, keeping the line endings, before passing it to `_split_sections`. Leave the rest of `parse` unchanged.
- `_criterion_text`: strip first, then refuse only if the stripped text contains `\n` or `\r`, with the same message. So `a\u2028b` is stored as given and `a\u2028` is stored as `a` (Python counts these characters as whitespace). Leading or trailing `\n` is stripped the same way, so `a\n` is stored as `a` (accepting unusual input over refusing it). Update the `with_criteria` docstring to match.

A trial of exactly this change (2026-11-25) broke only `test_new_criterion_rejects_all_line_breaks` in `tests/test_model.py`; narrow it to `\n` and `\r`.

Out of scope: frontmatter. Titles, labels and owners holding these characters keep today's behaviour (two earlier attempts that also changed frontmatter splitting exposed YAML and suggestion-inbox round-trip bugs; that is a separate ticket if wanted). Also out: History parsing (`transitions`, `timed_transitions`), `_text_lines`, `src/chitty/check.py`. Line numbers in parse errors keep counting frontmatter as today. A body line holding \u2028 before a heading marker is now one line, so the marker is not a heading; that matches CommonMark and is intended.

Tests, in a new `tests/test_criteria_line_breaks.py`, using Hypothesis with `examples(...)` from `tests/__init__.py`:

- Property: for a ticket drawn with `ticket_texts` from `tests/ticket_strategies.py` (filtered to tickets with criteria, as `tests/test_property_criterion_text.py` does), and a drawn text built from printable ASCII plus a module constant `OTHER_LINE_BREAKS` (the eight characters above), with at least one of those characters and non-empty after stripping: setting a drawn criterion to that text, then `render` and `parse`, gives `text.strip()` unticked there, and every other criterion keeps its text and tick.
- Example: a file whose Acceptance Criteria section holds `- [ ] a\u2028b` parses to one criterion `a\u2028b`, and `render` returns the input byte for byte.
- Example, in a class inheriting `CliTestCase` from `tests/test_cli.py`: `run_cli("add", "T", "-d", "x", "--ac", "one")`, then `run_cli("edit", "TASK-1", "--set-ac", "1", "a\u2028b")` exits 0, and `show TASK-1 --json` gives criterion text `a\u2028b`.

## Acceptance Criteria

- [x] The property and both examples in `tests/test_criteria_line_breaks.py` pass, and each fails with the `model.py` change reverted
- [x] Regression tests: `a\nb` and `a\rb` are still refused with `acceptance criterion must be a single line`; `test_new_criterion_rejects_all_line_breaks` (narrowed to `\n` and `\r`) and `make check` pass

## Plan

Add focused property, parser and CLI tests and confirm they fail before the fix; split only body lines on newline, narrow criterion validation, then run formatting and checks.

## Notes

Before the fix, all three new tests fail: parser rejects the split criterion, property rejects separator text, and CLI edit exits 1.

## Summary

Body parsing now splits only at LF; criterion edits trim before rejecting embedded CR or LF. New property, parser and CLI tests failed before the fix and pass after it; make check passes.

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
- 2026-11-24T09:27:12Z sunny-hazel-gannet planning → todo
- 2026-11-24T09:35:19Z open-pearl-raven todo → doing
- 2026-11-24T09:37:40Z open-pearl-raven: wrote the plan
- 2026-11-24T09:38:18Z open-pearl-raven: changed owner, notes
- 2026-11-24T09:38:18Z open-pearl-raven doing → planning
- 2026-11-25T11:34:54Z sunny-hazel-gannet: changed description, notes
- 2026-11-25T11:34:54Z sunny-hazel-gannet planning → todo
- 2026-11-25T12:11:52Z sunny-hazel-gannet: changed notes
- 2026-11-25T12:11:52Z sunny-hazel-gannet todo → planning
- 2026-11-25T21:07:08Z daring-ebony-wren: replaced notes; changed owner, description; wrote the plan
- 2026-11-25T21:07:13Z daring-ebony-wren: changed acceptance criteria
- 2026-11-25T21:07:31Z daring-ebony-wren: changed title
- 2026-11-25T21:07:31Z daring-ebony-wren planning → cold-read
- 2026-11-25T21:10:50Z daring-ebony-wren: changed description
- 2026-11-25T21:10:50Z daring-ebony-wren cold-read → planning
- 2026-11-25T21:10:56Z daring-ebony-wren planning → todo
- 2026-11-25T21:11:31Z mellow-yellow-jay todo → doing
- 2026-11-25T21:16:06Z mellow-yellow-jay: wrote the plan
- 2026-11-25T21:17:00Z mellow-yellow-jay: changed notes
- 2026-11-25T21:20:31Z daring-ebony-wren: changed acceptance criteria
- 2026-11-25T21:21:13Z mellow-yellow-jay: changed summary; ticked acceptance criteria
- 2026-11-25T21:23:40Z mellow-yellow-jay doing → review
