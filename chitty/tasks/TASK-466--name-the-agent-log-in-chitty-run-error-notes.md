---
title: Name the agent log in `chitty run` error notes
status: backlog
created: 2026-11-19
---

## Description

Follows `TASK-276`, which writes one log per ticket run. Plan once it lands. Agreed direction: `_record_ticket_error` (`src/chitty/run.py`) gains a required parameter `log_path: Path | None`; when it is not `None` (any error after the log was created), the note gets a line `` Log: `<path>` ``. This covers `agent timed out`, `agent exited with status N` and `<ID> was unchanged`, which on 2026-11-14 (circuitry) and 2026-11-19 (echonomicon) gave no clue why an agent did nothing. Test each of the three through `chitty run` with a fake agent.

## History

- 2026-11-19T21:18:58Z sunny-white-dormouse → backlog
