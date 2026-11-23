---
title: A `## Questions` section for open questions to a person (parent)
status: backlog
created: 2026-11-23
---

## Description

Parent for a built-in Questions section. Requested from a personal todo repository (2026-11-23) whose workflow is an agent interviewing the person: each item keeps open questions, asked in small batches later, and answers are recorded against them. Notes is append-only free text, so questions get lost there. Coding tickets need the same: planners and reviewers return tickets to `planning` with a "decision needed" note, and a structured list makes "what does this ticket need from a person?" queryable. The person agreed (2026-11-23) to build it.

Design (option 1 of the suggestion, which fits the strict schema): a `## Questions` section, a flat task list like Acceptance Criteria (`- [ ] question`), answered by ticking the item and recording the answer under it. Extra arbitrary `##` sections stay refused. Children: accept and validate the section; add and answer questions from the CLI and MCP; mark tickets with open questions in `chitty list`.

## Notes

Suggestion origin: /Users/singletoned/src/singletoned/todo

## History

- 2026-11-23T10:24:20Z witty-russet-gannet → backlog
- 2026-11-23T10:24:21Z witty-russet-gannet: changed notes
- 2026-11-23T10:40:11Z witty-russet-gannet: changed title, description
