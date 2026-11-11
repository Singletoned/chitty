---
title: Keep a log of each `chitty run` agent session
status: backlog
parent: TASK-275
created: 2026-11-11
---

## Description

- In print mode an agent prints only its final message, so nobody can see what it did. `chitty run` copies the agent's stdout and stderr to a log file per session, still printing them, and prints the log path when the session ends.
- Logs live in `<git common dir>/chitty/run/<ID>-<UTC time>.log`, never committed. At the start of each `chitty run`, delete logs there older than 30 days.

## Acceptance Criteria

- [ ] A `chitty run` whose fake agent prints `hello` writes a log containing `hello` under `<git common dir>/chitty/run/`, and prints its path. It fails today.
- [ ] A log there with a modification time 31 days ago is deleted by the next `chitty run`; one from 29 days ago is kept.

## History

- 2026-11-11T13:21:33Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:45Z vivid-yellowhammer: changed description, acceptance criteria
