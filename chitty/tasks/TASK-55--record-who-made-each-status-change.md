---
title: Record who made each status change
status: backlog
created: 2026-10-28
---

## Description

History records dates and status transitions but not who made them, so nothing shows whether a ticket's reviewer was also its author. Recording an actor (a person, or an agent session identifier) on each transition would make self-review visible, and could later let chitty refuse it. Open questions: where the identity comes from (git config, an env var such as CHITTY_ACTOR, or an MCP client name), and whether separate agent sessions can be told apart at all.

## Notes

Raised by the human; deferred ('maybe to track who does what, but not yet'). Pairs with the self-review ticket.

## History

- 2026-10-28 → backlog
