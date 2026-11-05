---
title: Stop telling workers to run `chitty inbox --pull`
status: doing
priority: medium
depends_on:
  - TASK-142
created: 2026-11-05
---

## Description

A worker's first step is `chitty inbox --pull`, from `src/chitty/roles/work.md` line 6 and `src/chitty/guide.md` line 8, which also reaches `AGENTS.md`'s managed block through `chitty init`. `chitty run` already pulls before it starts an agent (`src/chitty/run.py`), so this only spends a call. Seen on 2026-11-05 in a real session on `TASK-142`, where the human said it should not be doing that.

Remove the instruction from both files, leaving `chitty show <ID>` as the first step. In `work.md` the instruction wraps onto line 7, so rejoin the line, and keep each file's own word, `ticket` or `task`. Edit only this bullet: `TASK-173` also edits `work.md`, and `TASK-143` rewrites `guide.md`. No test expects the old text. `chitty list` already tells people when suggestions are waiting (`src/chitty/cli.py`), which covers manual sessions, and `review.md` and `plan.md` never had the instruction. `--pull` mentions in `src/chitty/cli.py` and `tests/test_cli.py` are other hints, and stay.

## Acceptance Criteria

- [x] `chitty guide work` and `chitty guide` no longer contain `inbox --pull`, shown by a test, and `chitty inbox --pull` itself still works
- [x] `AGENTS.md` no longer contains `inbox --pull`, after running `uv run chitty init` from the worktree, and `__version__` is bumped above `main`'s at the time of review

## Plan

Update the two managed worker-instruction source files only: remove the initial `chitty inbox --pull` wording while preserving each file’s existing `ticket`/`task` terminology and joining the wrapped `work.md` line. Bump the package patch version because `chitty init` output changes. Add or update focused tests proving both guides omit the pull instruction and that the inbox command remains functional, then run init and the required checks.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. Fixed: how to check `AGENTS.md`, the wrapped line, and who loses the pull, since `chitty list`'s hint covers them. Dependency on `TASK-142` kept, though soft: it is in review, and it bumps the same version. Rejected: mentioning that the pull is skipped on the first run after a project is added, which this change does not affect.

## History

- 2026-11-05T09:37:44Z mellow-newt → backlog
- 2026-11-05T09:40:00Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T09:40:01Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T09:40:02Z mellow-newt backlog → todo
- 2026-11-05T23:20:21Z open-dormouse todo → doing
- 2026-11-05T23:20:36Z open-dormouse: wrote the plan
- 2026-11-05T23:29:50Z open-dormouse: ticked acceptance criteria
- 2026-11-05T23:29:51Z open-dormouse: ticked acceptance criteria
