---
title: Add a machine-wide inbox for cross-project suggestions
status: todo
labels:
  - cli
depends_on:
  - TASK-29
created: 2026-10-27
---

## Description

Agents working in one project should be able to send ideas to another without knowing where it lives or touching its working tree. Modelled on sump: a machine-local inbox at ~/.local/share/chitty/inbox/<project>/, one Markdown file per suggestion (a task without an ID). Senders use chitty suggest PROJECT TITLE, where PROJECT is a project name or a repo path. Each repo collects its own with chitty pull, on its own branch through its normal autocommit/fix/format. The inbox is per machine.

## Acceptance Criteria

- [ ] Children done: project names and registration, suggest, pull, and removal of contexts.toml
- [ ] End-to-end by hand: an agent in one repo suggests to another by name and by path; pull there creates backlog tasks with provenance; the inbox is empty afterwards

## Notes

DECIDED with the human (2026-10-27): replace contexts.toml/add -c with the inbox; unknown names are an error pointing at --create rather than silently creating (but ideas for non-chitty projects, e.g. open source, must be receivable via --create); chitty init becomes idempotent (TASK-24) and doubles as the upgrade step; name clashes between repos are an error; commands are suggest and pull (pull is a little vague; revisit if a better verb appears).
