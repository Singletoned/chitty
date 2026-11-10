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

## Notes

Haiku cold read 1 (`refs/cold-read/TASK-248/1`) found the refusal already exists: `80ce143` (2026-11-09 21:08, released in 0.1.47) enforces a clean worktree on entering `review` and `done`. The mullion handoffs were at 20:39 to 20:43 the same evening, before it landed. The only gap the read found was that changes under `chitty/` also block. Outcome: no change; `chitty run` and `chitty check` block on them too, so blocking stays consistent. Archived as already done.

## History

- 2026-11-10T19:32:56Z jolly-heron → backlog
- 2026-11-10T19:37:36Z jolly-heron: changed notes
