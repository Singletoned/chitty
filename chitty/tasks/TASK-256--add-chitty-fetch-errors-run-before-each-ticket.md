---
title: Add `chitty fetch-errors`, run before each ticket
status: backlog
labels:
  - plan-next
created: 2026-11-11
---

## Description

- `chitty fetch-errors` runs a configured command, which may check several sources (Sump, CI).
- No errors: does nothing.
- Errors: starts a worker on a stronger model than the usual workers (configured). It dedupes the errors with tools, then for each:
  - small bug (for example, a test failing for a silly reason): a bug ticket that the next `chitty run` picks up;
  - anything needing a human decision: a `backlog` ticket.
- `chitty run` calls it before choosing a ticket.
- Open: small bugs should beat every `todo` ticket, but priority tops out at `high`. Add `urgent`, or rank `bug`-labelled tickets first?

## History

- 2026-11-11T10:02:52Z jolly-heron → backlog
