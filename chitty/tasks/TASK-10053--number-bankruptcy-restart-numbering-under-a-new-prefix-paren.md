---
title: "Number bankruptcy: restart numbering under a new prefix (parent)"
status: backlog
labels:
  - needs-minor
created: 2026-11-26
moved_from: TASK-W74AVC
---

## Description

Ticket numbers grow without bound; this repository's jumped to `TASK-10000`. The person asked for "a number bankruptcy system where we start again", and chose (2026-11-26) to start under a new prefix rather than reuse numbers: every old ID stays unique, so commit messages, `task-<n>` branch names and other repositories' citations stay correct, and nothing is rewritten.

Design: a context gets `old_prefixes` in `chitty.toml`. Tickets with an old prefix stay readable, linkable and listed; new IDs use only `prefix`, starting at 1. Starting again is a config change a person makes on `main`: set `prefix` to the new prefix and add the old one to `old_prefixes`. The children: the setting and its validation, reading old-prefix tickets everywhere, and numbering only the current prefix.

## Acceptance Criteria

- [ ] All child tickets are done.

## History

- 2026-11-26T11:11:53Z calm-ochre-quail → backlog
- 2026-11-26T17:50:32Z calm-ochre-quail: changed title, labels, description, acceptance criteria
- 2026-11-26T17:50:32Z calm-ochre-quail backlog → cold-read
- 2026-11-26T17:52:00Z calm-ochre-quail: changed title, description, acceptance criteria
- 2026-11-26T17:52:00Z calm-ochre-quail cold-read → backlog
- 2026-11-26T20:30:10Z intrepid-russet-falcon: renumbered from TASK-W74AVC
