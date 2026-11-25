---
title: "Planning guide: give wrong versions as literal edits with checked expected failures"
status: backlog
created: 2026-11-25
provisional: true
---

## Description

In echonomicon, TASK-213 returned to planning three times on 2026-11-24 (worker openai-codex/gpt-6-luna). Its wrong versions were prose ('including it in the desired objects without writing it'), and the worker could not turn them into code. The ticket's expected failure for one of them (FileNotFoundError) was also wrong: the code skips a missing file through an is_file() check, so the real failure is an assertion. The planner repeated that mistake in a note. After the section was rewritten as exact one-line edits (old line to new line, naming the function where a line occurs twice), each with its expected failing assertion, a cold reader applied every edit to a copy and confirmed each failure. Suggest that the planning guide ask for each wrong version of existing code as a literal edit with its expected failure, verified against the code (ideally by the cold reader running it in a scratch copy), rather than a description.

## Notes

Suggestion origin: echonomicon

Triage 2026-11-25: obsolete. `chitty guide plan` no longer asks for wrong versions (`grep -ri "wrong version" src/chitty` finds nothing); mutation testing in review is TASK-594.

## History

- 2026-11-25T22:28:23Z calm-ochre-quail → backlog
- 2026-11-25T22:28:25Z calm-ochre-quail: changed notes
- 2026-11-25T22:33:13Z calm-ochre-quail: changed notes
- 2026-11-25T22:33:15Z calm-ochre-quail backlog → archived
