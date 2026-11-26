---
title: Runner blames `main` for a check failure caused by uncommitted changes in the ticket worktree
status: backlog
created: 2026-11-26
provisional: true
---

## Description

On 2026-11-24, `chitty run` set TASK-651 to `error` with: "check exited with status 2; output in `.chitty/check.log`; the branch has no work yet, so `main` fails this check". `main` passed `make check` (verified 2026-11-26: 1237 passed). The failure came from uncommitted partial work left in `.worktrees/task-651` (`src/chitty/store.py`, `tests/test_next.py` and others, all modified), which made `tests/test_next.py::TestNext::test_run_review_compares_only_tool_chitty_in_pyproject` fail. The branch had only ticket-edit commits, so the runner concluded that `main` was broken. Suggested fix: before blaming `main`, check whether the worktree is dirty (`git status --porcelain`). If it is, say that the check failed on uncommitted changes in the worktree. Possibly also refuse to check a dirty worktree at all. The wrong message sent planners looking for a broken `main`.

## Notes

Suggestion origin: chitty

Already fixed: commit af2680bc (TASK-676, 2026-11-26) makes `_run_check` in `src/chitty/run.py` record the worktree's uncommitted paths before the check and report them instead of blaming `main`.

## History

- 2026-11-26T18:06:09Z calm-ochre-quail → backlog
- 2026-11-26T18:06:12Z calm-ochre-quail: changed notes
- 2026-11-26T18:07:18Z calm-ochre-quail: changed notes
- 2026-11-26T18:07:21Z calm-ochre-quail backlog → archived
