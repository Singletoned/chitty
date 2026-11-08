---
title: Warn in `chitty check` about indented lines inside a paragraph
status: doing
created: 2026-11-05
---

## Description

Seen in `echonomicon`. Agents paste command output into `--note` and `--summary` as plain lines, for example a `mate check` log with `  Using cached ad detection: ...` indented by two spaces. To Markdown that is a continuation of the paragraph above, so formatters such as `prettier` (run by `taidy`) strip the indentation and reflow it. Every format run in any branch then rewrites other tickets' notes, and an agent either commits someone else's changes or restores them by hand.

Decision: `chitty check` warns about these lines, the same way `_markdown_warnings` in `src/chitty/check.py` already warns about a literal `*` or `_`. The rule:

- For each field in `MARKDOWN_FIELDS` (`Description`, `Plan`, `Notes`, `Summary`), parse the text with the module's `MARKDOWN` parser (`MARKDOWN.parse`, block-level, not `parseInline`).
- For each `paragraph_open` token with `level == 0` (a top-level paragraph, not one inside a list or block quote), look at its source lines, `text.split("\n")[token.map[0]:token.map[1]]` (not `splitlines()`, which also splits on form feeds and other characters that markdown-it does not count as line ends). If any line after the first starts with a space or tab, report one warning for that field.
- Message: `{field} has an indented line inside a paragraph; put pasted output in a fenced code block`, severity `warning`.

One warning per field is enough, as the delimiter warning does once per character. Lines inside fenced code blocks, indented code blocks (four spaces after a blank line), and list items are not top-level paragraphs, so they are not reported.

Add the tests to `tests/test_check.py`, next to the delimiter-warning tests, writing the task file directly as those tests do. `StoreTestCase.add` has no way to set Notes, so insert a `## Notes` section before `## History`, which must stay the last section.

Three archived tickets (`TASK-124`, `TASK-126`, `TASK-129`) have unfenced pasted `git` output in their Notes, so `chitty check` will warn about them. That is correct; leave those files alone.

Out of scope: other ways pasted output gets rewritten that this rule does not catch, such as an indented line that starts a list (`  - item`) or a heading underline (`  ---`); guidance telling agents to fence output, rewriting or rejecting notes on write, paragraphs inside lists, and acceptance criteria text.

## Acceptance Criteria

- [ ] A test writes a ticket whose Notes have a paragraph with a two-space-indented second line and asserts exactly one warning with the message in the description; the worker records that it failed before the change
- [ ] A test shows no warning for the same output in a fenced code block, an indented code block, or a numbered list item with an indented continuation line

## Notes

Suggestion origin: echonomicon

Cold read by a fresh Haiku subagent, 2026-11-07, kept as `refs/cold-read/TASK-198/1`. It built the ticket from the description alone: the warning test failed first (`Lists differ: [] != ['warning']`), then passed, and `make check` passed. On this repo's tickets it found three true positives, all in archived tickets, and no false positives. Outcomes:

- Fixed: `text.splitlines()` disagrees with markdown-it's line numbers when the text has a form feed or similar character, so a real case was missed. The description now says `text.split("\n")`.
- Fixed: the test helper cannot write Notes, and `## History` must stay last. The description now says to insert `## Notes` before it.
- Fixed: the three archived warnings (`TASK-124`, `TASK-126`, `TASK-129`) are expected and left alone; now stated.
- Rejected, stated as out of scope: an indented line that starts a list or a setext underline is rewritten by `prettier` but not caught. They are separate Markdown constructs, and the common case, indented log lines, is caught.
- Confirmed: hard breaks and deeper indents inside a paragraph are reported, and `prettier` does rewrite them, so those warnings are right.
- Not a problem: "Deleted branch task-2" in the `make check` log comes from a test's temporary repository; this repository has no such branch.
- None of these changes the design, so no second read.

## History

- 2026-11-05T19:11:12Z youthful-toad → backlog
- 2026-11-05T19:11:12Z youthful-toad: changed notes
- 2026-11-07T09:16:06Z vivid-dormouse: changed description, acceptance criteria
- 2026-11-07T09:16:15Z vivid-dormouse: changed title
- 2026-11-07T09:20:21Z vivid-dormouse: changed description, notes
- 2026-11-07T09:20:21Z vivid-dormouse backlog → todo
- 2026-11-08T11:17:07Z quick-dormouse todo → doing
