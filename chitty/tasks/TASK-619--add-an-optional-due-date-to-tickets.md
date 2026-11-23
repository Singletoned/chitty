---
title: Add an optional due date to tickets
status: backlog
created: 2026-11-23
---

## Description

Context: a personal todo repo (~/src/singletoned/todo) uses agents to manage the user's life todos as one Markdown file per item with YAML frontmatter, the same model as Chitty. Chitty was assessed for it on 2026-11-23 and not adopted, mainly because tickets cannot record a deadline: frontmatter is strict and has no date field besides `created`.

Examples of real todos with deadlines: list a football ticket on an exchange before the match on 2026-11-24; bake cakes on 2026-11-23. Coding tickets have deadlines too (releases, external dates), so this is not specific to personal use.

Proposal: an optional `due` key (ISO 8601 date, written unquoted like `created`). `chitty check` validates it. `chitty add/edit --due DATE` (and a way to clear it). `chitty list` could show it and sort or filter by it (e.g. `--due-before DATE`); `chitty next` might weigh overdue tickets first, but that can be a later decision.

Acceptance idea: a ticket with `due: 2026-11-24` round-trips through prettier and mdformat unchanged and validates; a malformed date fails `chitty check` with a clear message.

## Notes

Suggestion origin: /Users/singletoned/src/singletoned/todo

## History

- 2026-11-23T10:24:16Z witty-russet-gannet → backlog
- 2026-11-23T10:24:18Z witty-russet-gannet: changed notes
