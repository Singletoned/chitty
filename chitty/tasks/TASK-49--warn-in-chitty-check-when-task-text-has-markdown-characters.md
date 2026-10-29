---
title: Warn in chitty check when task text has Markdown characters a formatter will escape
status: doing
created: 2026-10-28
---

## Description

Bare *, _ and similar characters that render as literal text (e.g. 'static/photos/*.jpg') get rewritten by formatters (\*), causing diffs and showing that the text should have been a code span. chitty check could warn, without failing, for each such character in task text and suggest backticks. To avoid a guessing heuristic, use a CommonMark parser (markdown-it-py, which mdformat uses) to find delimiter characters that end up as literal text; that is exactly the set formatters escape. Open questions: check has no warning severity yet (check/fix are error-only, and fix fails on any problem), and this adds a dependency.

## Acceptance Criteria

- [x] check reports a warning, not an error, naming task, field and character for each delimiter that parses as literal text outside code spans; exit status is unaffected
- [x] Intentional emphasis, links and code spans produce no warning
- [x] fix does not fail on warnings
- [x] Tests cover a glob, snake_case words, emphasis and code spans; PLAN.md describes warning severity

## Plan

Inspect existing Markdown parsing and check reporting. Add warnings for literal delimiter characters outside code spans without changing check or fix exit behavior, cover the required glob, snake_case, emphasis and code-span cases, update PLAN warning severity, then run `make check` and hand off for review.

## Notes

Raised by the human while refining TASK-47. Needs a decision on adding warning severity to check and the markdown-it-py dependency.

Promoted by the human: add a non-failing warning severity to check and the markdown-it-py dependency.

Review failed. (1) False positives: the description says to warn for exactly the set formatters escape, but every literal `*`/`_` is flagged. Checked mdformat: it escapes `static/photos/*.jpg` but leaves `snake_case`, `depends_on` and `a * b` alone. Prettier also leaves `snake_case` alone. `chitty check` in this repo prints 96 warnings, mostly intraword `_`, and one identical line per character. Narrow the warnings to delimiters a formatter would escape, and collapse repeats to one per field and character. The current test asserts a `snake_case` warning, so it needs a human decision on whether `snake_case` should warn at all. (2) The MCP `check` and `fix` tools in `mcp.py` drop `severity`, so MCP clients cannot tell warnings from errors, and the two front ends diverge. (3) `markdown-it-py==3.0.0` is an exact pin in a library dependency; prefer a lower bound unless there is a reason.

Decided with the human: `snake_case` and other words with `_` inside them should not warn. The `snake_case` test should assert no warning.

## Summary

Added runtime `markdown-it-py` parsing and advisory warning diagnostics for literal `*` and `_` delimiters. Errors alone now determine `check`, `fix`, and autocommit failure; warnings are printed and included in JSON. Added Markdown and CLI coverage and documented warning severity. Verified with `make check`.

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
- 2026-10-29 review → doing
