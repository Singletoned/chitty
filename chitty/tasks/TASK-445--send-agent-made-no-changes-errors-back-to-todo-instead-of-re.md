---
title: Send "agent made no changes" errors back to todo instead of repair
status: backlog
created: 2026-11-19
---

## Description

In echonomicon TASK-161 the first run went to `error` with "TASK-161 was unchanged; only committed changes are visible to `chitty run`". The cause was a misconfigured `agent_command` that exited 0 without doing anything. `chitty run --errors` then gave it to a repair agent, but there was nothing to repair: the whole ticket still had to be implemented. The repair prompt (fix the reported failure, then review or blocked) does not fit a full implementation, and the agent (gpt-6-luna via pi) stopped halfway with no tests and failing checks. Suggestion: when an error means the work agent made no commits and the branch equals main, return the ticket to `todo` (with a note) instead of sending it to repair. Or have the repair prompt say that an untouched branch means implementing the ticket in full, as a work session would.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-19T20:55:18Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:19Z sunny-white-dormouse: changed notes
