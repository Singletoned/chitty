---
title: Refuse `chitty edit -s review` while the worktree has uncommitted changes
status: backlog
created: 2026-11-10
---

## Description

In mullion (TASK-2, 2026-11-09), two workers moved the ticket to `review` with all their work left untracked in `tests/harness/`, although the work guide says `git status --short` must be empty first. Both reviews then failed on the uncommitted files, wasting a review each.

Make `chitty edit -s review` (and the MCP equivalent) refuse when the working tree of the checkout it runs in has uncommitted or untracked changes outside `chitty/`. The ticket file itself is about to be autocommitted, so changes under `chitty/` do not count. The error lists the paths, as `git status --short` would, and says to commit them first. Nothing is written. Every other status change is unaffected. Put the check outside `cli.py` and `mcp.py`.

Update the work guide's handoff step to mention the refusal, and the relevant section of `PLAN.md`.

## Acceptance Criteria

- [ ] In a repository with an untracked `tests/new_test.py`, `chitty edit <ID> -s review` exits non-zero, names `tests/new_test.py`, and leaves the ticket file and `git log` unchanged; after the file is committed, the same command moves the ticket to `review`.
- [ ] An uncommitted change under `chitty/` alone does not block the move, and `chitty edit <ID> -s doing` succeeds with untracked files present.

## History

- 2026-11-10T19:32:56Z jolly-heron → backlog
