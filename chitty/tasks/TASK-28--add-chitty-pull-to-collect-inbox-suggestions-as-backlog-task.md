---
title: Add chitty pull to collect inbox suggestions as backlog tasks
status: todo
labels:
  - cli
depends_on:
  - TASK-27
parent: TASK-25
created: 2026-10-27
---

## Description

chitty pull, run in a repo, turns each waiting suggestion for its project into a backlog task in the default context and removes it from the inbox.

## Acceptance Criteria

- [ ] Each suggestion becomes a backlog task (default Description if none given) with a note recording its origin
- [ ] Each file is moved aside before processing and removed only after its task is written, so nothing is lost and two concurrent pulls cannot import it twice
- [ ] Registers the project if it is not yet registered
- [ ] Follows autocommit (one commit for the batch), fix and autoformat like any other write
- [ ] With nothing waiting it says so and exits zero
- [ ] chitty list prints a one-line stderr reminder when suggestions are waiting for this project
- [ ] MCP pull tool
- [ ] Tests, PLAN.md, README and the agent guide (pull at the start of a session) updated
