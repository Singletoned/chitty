---
title: Warn in chitty check when task text has Markdown characters a formatter will escape
status: backlog
created: 2026-10-28
---

## Description

Bare *, _ and similar characters that render as literal text (e.g. 'static/photos/*.jpg') get rewritten by formatters (\*), causing diffs and showing that the text should have been a code span. chitty check could warn, without failing, for each such character in task text and suggest backticks. To avoid a guessing heuristic, use a CommonMark parser (markdown-it-py, which mdformat uses) to find delimiter characters that end up as literal text; that is exactly the set formatters escape. Open questions: check has no warning severity yet (check/fix are error-only, and fix fails on any problem), and this adds a dependency.

## Acceptance Criteria

- [ ] check reports a warning, not an error, naming task, field and character for each delimiter that parses as literal text outside code spans; exit status is unaffected
- [ ] Intentional emphasis, links and code spans produce no warning
- [ ] fix does not fail on warnings
- [ ] Tests cover a glob, snake_case words, emphasis and code spans; PLAN.md describes warning severity

## Notes

Raised by the human while refining TASK-47. Needs a decision on adding warning severity to check and the markdown-it-py dependency.

## History

- 2026-10-28 → backlog
