---
title: Skip `cold-read/*` branches when reading tickets from Git
status: review
parent: TASK-259
created: 2026-11-11
---

## Description

- Ticket discovery reads every branch under `refs/heads` and `refs/remotes` (`historical_files` in `src/chitty/git.py`). Skip branches named `cold-read/*`, local or on any remote, before both its log and tree reads.
- Only `historical_files` changes; `local_branches` and `has_local_branch` stay as they are.
- Cold reads run on these branches (TASK-259) and must never be a source of ticket state.

## Acceptance Criteria

- [x] A test makes branch `cold-read/task-1/1` with a copy of `TASK-1` committed later than `main`'s (set `GIT_COMMITTER_DATE`), and `chitty show TASK-1` prints `main`'s version. It fails today.
- [x] The same holds for a remote-tracking branch `origin/cold-read/task-1/1`.

## Plan

Add CLI regression tests for newer local and remote-tracking cold-read refs and run them before the fix. Update only historical_files ref filtering so cold-read branches are excluded before Git log/tree reads. Run make format and make check, then commit the implementation.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-268/1`. Check it against the current criteria; do not trust it.

Both regression tests failed before the fix, each selecting the cold-read copy; both pass after filtering local and remote-tracking cold-read refs before historical reads. make format and make check pass.

## Summary

Handoff: historical_files excludes cold-read branches before ticket history reads. Verification: local and remote regression tests failed pre-fix and passed with make check; format passed. No follow-up needed.

## History

- 2026-11-11T13:21:05Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:41Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T13:39:49Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:42:50Z vivid-yellowhammer: changed description, acceptance criteria, notes
- 2026-11-11T13:42:50Z vivid-yellowhammer cold-read → todo
- 2026-11-11T14:09:06Z able-gannet todo → doing
- 2026-11-11T14:09:36Z able-gannet: wrote the plan
- 2026-11-11T14:11:13Z able-gannet: changed notes, summary; ticked acceptance criteria
- 2026-11-11T14:11:13Z able-gannet doing → review
