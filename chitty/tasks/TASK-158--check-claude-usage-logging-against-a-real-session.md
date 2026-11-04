---
title: Check `claude` usage logging against a real session
status: backlog
priority: medium
owner: human
depends_on:
  - TASK-155
  - TASK-157
parent: TASK-106
created: 2026-11-04
---

## Description

The planning session adds the `--settings` part from `TASK-157` to this repository's `claude` entry. The human then runs `chitty run --agent claude` from an ordinary shell, because a worker cannot start `claude`, and the planning session compares the log line with the session's transcript, counting each `message.id` once. Check that `SessionEnd` fires under `-p`, and that `claude` exits normally afterwards. A difference of more than 5% means a call is missing, so say what is missing rather than adjusting for it.

## Acceptance Criteria

- [ ] A note records the real log line, the transcript's sum and any difference, and that the hook fired under `-p`

## History

- 2026-11-04T18:01:19Z mellow-newt → backlog
