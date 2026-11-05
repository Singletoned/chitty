---
title: Keep pasted command output fenced in task notes
status: backlog
created: 2026-11-05
---

## Description

Seen in `echonomicon`. Agents paste command output into `--note` and `--summary` as plain lines, for example a `mate check` log with `  Using cached ad detection: ...` indented by two spaces. To Markdown that is paragraph text, so formatters such as `prettier` (run by `taidy`) strip the indentation and reflow it. Every `mate check` in any branch then rewrites other tickets' notes (`TASK-25` and `TASK-30` there), and an agent either commits someone else's changes or restores them by hand. A formatter cannot reliably tell pasted output from prose, but it leaves fenced code blocks alone, so the fix belongs where the note is written.

Options:
1. Guidance in `chitty guide` and the generated agent guidance: put pasted output in fenced code blocks, or summarise it rather than pasting it.
2. `chitty check` warns about a note line that starts with whitespace outside a fence, as it already warns about a literal `_` outside backticks.
3. On write, `chitty edit` fences a run of indented lines automatically, or rejects the note with a hint.
Option 2 is the cheapest guard. Option 1 stops most cases. `taidy` has a matching suggestion to skip tool-owned files such as `chitty/` task files, which would protect existing notes.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-05T19:11:12Z youthful-toad → backlog
- 2026-11-05T19:11:12Z youthful-toad: changed notes
