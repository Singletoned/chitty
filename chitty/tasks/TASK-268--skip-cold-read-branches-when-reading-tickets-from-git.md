---
title: Skip `cold-read/*` branches when reading tickets from Git
status: cold-read
parent: TASK-259
created: 2026-11-11
---

## Description

- Ticket discovery reads every branch under `refs/heads` and `refs/remotes` (`src/chitty/git.py`, the `for-each-ref` call). Skip branches named `cold-read/*`, local or remote.
- Cold reads run on these branches (TASK-259) and must never be a source of ticket state.

## Acceptance Criteria

- [ ] A test makes branch `cold-read/task-1/1` with a newer copy of `TASK-1` than `main`, and `chitty show TASK-1` prints `main`'s version. It fails today.
- [ ] The same holds for a remote-tracking branch `origin/cold-read/task-1/1`.

## History

- 2026-11-11T13:21:05Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:41Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T13:39:49Z vivid-yellowhammer backlog → cold-read
