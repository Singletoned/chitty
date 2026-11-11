---
title: Skip `cold-read/*` branches when reading tickets from Git
status: todo
parent: TASK-259
created: 2026-11-11
---

## Description

- Ticket discovery reads every branch under `refs/heads` and `refs/remotes` (`historical_files` in `src/chitty/git.py`). Skip branches named `cold-read/*`, local or on any remote, before both its log and tree reads.
- Only `historical_files` changes; `local_branches` and `has_local_branch` stay as they are.
- Cold reads run on these branches (TASK-259) and must never be a source of ticket state.

## Acceptance Criteria

- [ ] A test makes branch `cold-read/task-1/1` with a copy of `TASK-1` committed later than `main`'s (set `GIT_COMMITTER_DATE`), and `chitty show TASK-1` prints `main`'s version. It fails today.
- [ ] The same holds for a remote-tracking branch `origin/cold-read/task-1/1`.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-268/1`. Check it against the current criteria; do not trust it.

## History

- 2026-11-11T13:21:05Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:41Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T13:39:49Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:42:50Z vivid-yellowhammer: changed description, acceptance criteria, notes
- 2026-11-11T13:42:50Z vivid-yellowhammer cold-read → todo
