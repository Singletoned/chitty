---
title: Add chitty pull to collect inbox suggestions as backlog tasks
status: done
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

- [x] Each suggestion becomes a backlog task (default Description if none given) with a note recording its origin
- [x] Each file is moved aside before processing and removed only after its task is written, so nothing is lost and two concurrent pulls cannot import it twice
- [x] Registers the project if it is not yet registered
- [x] Follows autocommit (one commit for the batch), fix and autoformat like any other write
- [x] With nothing waiting it says so and exits zero
- [x] chitty list prints a one-line stderr reminder when suggestions are waiting for this project
- [x] MCP pull tool
- [x] Tests, PLAN.md, README and the agent guide (pull at the start of a session) updated

## Plan

Implement safe inbox-claim and suggestion parsing, create default-context backlog tasks through Repo, add CLI/MCP commands and waiting reminders, then verify with isolated inbox tests.

## Notes

Pull now atomically claims suggestions, creates provenance-backed backlog tasks, registers the project, uses one normal finalization/autocommit batch, exposes CLI/MCP/reminders, and is documented/tested. Full make check passes.
