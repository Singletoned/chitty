---
title: Skip `cold-read/*` branches when reading tickets from Git
status: backlog
parent: TASK-259
created: 2026-11-11
---

## Description

- Ticket discovery reads every branch under `refs/heads` and `refs/remotes` (`src/chitty/git.py`, the `for-each-ref` call). Skip branches named `cold-read/*`, local or remote.
- Cold reads run on these branches (TASK-259) and must never be a source of ticket state.

## History

- 2026-11-11T13:21:05Z vivid-yellowhammer → backlog
