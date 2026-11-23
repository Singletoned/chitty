---
title: "Allow a Questions section (or extra ## sections) in tickets"
status: backlog
created: 2026-11-23
---

## Description

Context: a personal todo repo (~/src/singletoned/todo) manages the user's todos as Markdown files with YAML frontmatter, close to Chitty's format. Assessed 2026-11-23 and not adopted, partly because Chitty rejects any `##` section other than Description, Acceptance Criteria, Plan, Notes, Summary and History.

That repo's core workflow is an agent interviewing the user: each item keeps an `## Open questions` checklist (`- [ ] question`), questions are asked in small batches later, and answers are recorded by ticking the item and writing the answer. Notes is append-only free text, so questions get lost there, and Acceptance Criteria means something different.

The same need exists for coding tickets: planners and reviewers often have unresolved questions for the human (Chitty already returns tickets to `planning` with a "decision needed" note). A structured questions list would make "what does this ticket need from a person?" queryable.

Options, smallest first:
1. A built-in `## Questions` section: flat task list like Acceptance Criteria, with `edit --question TEXT` / `--answer N TEXT` (ticks it and appends the answer), and `list` marking tickets with open questions.
2. A config setting that allows named extra sections, kept as free Markdown and preserved byte-for-byte.

Option 1 fits Chitty's strict-schema principle better; option 2 is more general.

## Notes

Suggestion origin: /Users/singletoned/src/singletoned/todo

## History

- 2026-11-23T10:24:20Z witty-russet-gannet → backlog
- 2026-11-23T10:24:21Z witty-russet-gannet: changed notes
