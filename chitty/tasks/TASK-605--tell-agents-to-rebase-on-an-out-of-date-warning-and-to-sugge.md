---
title: Tell agents to rebase on an out-of-date warning, and to suggest rather than file tickets
status: backlog
depends_on:
  - TASK-602
created: 2026-11-23
---

## Description

Decided with the person, 2026-11-23: Chitty warns rather than refuses when a ticket's copy on this branch is out of date (`TASK-602`). The agent instructions must say what to do. To be planned: in the work, review, plan and cold-read guides, say that a warning that another branch changed the ticket means rebase onto `main` (or onto the ticket's branch) and read it again. In the work guide, also say that a worker who finds something unrelated files it with `chitty suggest` when it is small, and returns its ticket to `planning` when it is big; it does not create tickets on its own branch. (In the 30 days to 2026-11-23, none of 419 ticket adds on `main` came from another ticket's branch.) Keep the advice general, as `AGENTS.md` asks for guide text.

## History

- 2026-11-23T08:47:14Z plucky-umber-wren → backlog
