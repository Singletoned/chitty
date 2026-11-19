---
title: Mark tickets returned to `planning` in `chitty list`, apart from the planning queue
status: backlog
created: 2026-11-19
---

## Description

Owner request 2026-11-19: a ticket a worker or reviewer sent back to `planning` because it needs fixing looks the same as one waiting in the long planning queue, so returned tickets wait unnoticed (`TASK-373`, `TASK-408` and `TASK-413` on 2026-11-19).

Proposed, to confirm when planning: derive it from History, with nothing to set or clear. A ticket in `planning` is returned when its last move into `planning` came from `doing`, `review`, `blocked` or `error`. `chitty list` marks it (for example `↩`) and lists returned tickets before the rest of `planning`; `chitty list --json` gains a boolean `returned`. Moving it on to `cold-read` or `todo` ends it. Make the rule a pure function of the parsed History.

## History

- 2026-11-19T13:59:45Z quick-ginger-lapwing → backlog
