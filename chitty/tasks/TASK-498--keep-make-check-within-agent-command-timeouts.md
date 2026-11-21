---
title: Keep `make check` within agent command timeouts
status: backlog
created: 2026-11-21
---

## Description

Seen 2026-11-21 on TASK-482: the worker's `make check` "timed out after 120 seconds during unittest", so it could not verify its work and returned the ticket. On 2026-11-20 TASK-453's runner check reported `Ran 867 tests in 115.332s`, and TASK-479's `Ran 868 tests in 65.308s`. The suite sits right at the 120-second default timeout of agent shell tools, and it grows with every ticket.

Options: run the unit tests in parallel (for example with `unittest-parallel` or a `make check` that splits test modules across processes), find and speed up the slowest real-Git tests, or have `chitty guide work` tell workers to run `make check` with a longer timeout or in the background. A test of the suite's own duration would keep it from creeping back.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:58:02Z nimble-umber-gannet → backlog
- 2026-11-21T07:58:03Z nimble-umber-gannet: changed notes
