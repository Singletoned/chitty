---
title: Warn in `chitty check` about indented lines inside a paragraph
status: backlog
created: 2026-11-05
---

## Description

Seen in `echonomicon`. Agents paste command output into `--note` and `--summary` as plain lines, for example a `mate check` log with `  Using cached ad detection: ...` indented by two spaces. To Markdown that is a continuation of the paragraph above, so formatters such as `prettier` (run by `taidy`) strip the indentation and reflow it. Every format run in any branch then rewrites other tickets' notes, and an agent either commits someone else's changes or restores them by hand.

Decision: `chitty check` warns about these lines, the same way `_markdown_warnings` in `src/chitty/check.py` already warns about a literal `*` or `_`. The rule:

- For each field in `MARKDOWN_FIELDS` (`Description`, `Plan`, `Notes`, `Summary`), parse the text with the module's `MARKDOWN` parser (`MARKDOWN.parse`, block-level, not `parseInline`).
- For each `paragraph_open` token with `level == 0` (a top-level paragraph, not one inside a list or block quote), look at its source lines, `text.splitlines()[token.map[0]:token.map[1]]`. If any line after the first starts with a space or tab, report one warning for that field.
- Message: `{field} has an indented line inside a paragraph; put pasted output in a fenced code block`, severity `warning`.

One warning per field is enough, as the delimiter warning does once per character. Lines inside fenced code blocks, indented code blocks (four spaces after a blank line), and list items are not top-level paragraphs, so they are not reported.

Add the tests to `tests/test_check.py`, next to the delimiter-warning tests, writing the task file directly as those tests do.

Out of scope: guidance telling agents to fence output, rewriting or rejecting notes on write, paragraphs inside lists, and acceptance criteria text.

## Acceptance Criteria

- [ ] A test writes a ticket whose Notes have a paragraph with a two-space-indented second line and asserts exactly one warning with the message in the description; the worker records that it failed before the change
- [ ] A test shows no warning for the same output in a fenced code block, an indented code block, or a numbered list item with an indented continuation line

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-05T19:11:12Z youthful-toad → backlog
- 2026-11-05T19:11:12Z youthful-toad: changed notes
- 2026-11-07T09:16:06Z vivid-dormouse: changed description, acceptance criteria
- 2026-11-07T09:16:15Z vivid-dormouse: changed title
