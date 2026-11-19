---
title: Record why an agent run ended with no changes
status: backlog
created: 2026-11-19
---

## Description

In circuitry on 2026-11-14 between 09:16 and 09:23, four tickets (CIRCUIT-97, 105, 106, 107) each went to error with only `<ID> was unchanged; only committed changes are visible to chitty run`. The `pi` session directories for those worktrees were empty, so nothing showed why the agent did no work. Expected: capture the agent exit code and the tail of its stdout/stderr in the error note, and probably stop `--loop` after the first such failure, not use up every todo ticket.

## Notes

Suggestion origin: circuitry

## History

- 2026-11-19T20:55:13Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:14Z sunny-white-dormouse: changed notes
