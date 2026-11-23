---
title: Optional due dates on tickets (parent)
status: backlog
created: 2026-11-23
---

## Description

Parent for due-date support. Requested from a personal todo repository (2026-11-23) that could not adopt Chitty because tickets cannot record a deadline; coding tickets have deadlines too (releases, external dates). The person agreed (2026-11-23) to build it.

Design: an optional frontmatter key `due`, an ISO 8601 date written unquoted like `created`. Children, in order: the key and its validation; setting and clearing it from the CLI and MCP; showing, sorting and filtering by it in `chitty list`. Whether `chitty next` should prefer overdue tickets is left for later.

## Notes

Suggestion origin: /Users/singletoned/src/singletoned/todo

## History

- 2026-11-23T10:24:16Z witty-russet-gannet → backlog
- 2026-11-23T10:24:18Z witty-russet-gannet: changed notes
- 2026-11-23T10:39:44Z witty-russet-gannet: changed title, description
