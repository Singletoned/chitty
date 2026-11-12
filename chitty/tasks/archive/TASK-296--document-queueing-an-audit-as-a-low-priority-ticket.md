---
title: Document queueing an audit as a low-priority ticket
status: backlog
depends_on:
  - TASK-291
parent: TASK-290
created: 2026-11-11
---

## Description

- The human runs the audit now and then, by adding a `low` ticket, which `chitty next` already sorts after every other `todo` ticket. A worker picks it up when nothing else is waiting and runs `make audit`.
- In `README.md`, add the `chitty add` command for that ticket, with a description telling the worker to run `make audit` and set the ticket to `review` with the number of suggestions sent.

## Acceptance Criteria

- [ ] `README.md` shows the command, and it creates a `low` `todo` ticket.

## Notes

Withdrawn 2026-11-11: the human runs `make audit` by hand for now.

## History

- 2026-11-11T16:18:28Z vivid-yellowhammer → backlog
- 2026-11-11T18:50:45Z vivid-yellowhammer: changed title, owner, description, acceptance criteria
- 2026-11-11T18:59:39Z vivid-yellowhammer: changed notes
- 2026-11-11T18:59:40Z vivid-yellowhammer backlog → archived
