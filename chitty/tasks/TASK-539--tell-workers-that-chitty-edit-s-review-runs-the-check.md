---
title: Tell workers that `chitty edit -s review` runs the check
status: todo
depends_on:
  - TASK-538
created: 2026-11-22
---

## Description

Replaces the second half of `TASK-343`. After `TASK-538`, `chitty edit -s review` runs the configured check itself, so the work guide need not tell workers to run it.

In `src/chitty/roles/work.md`, replace the sentence that tells workers to run `chitty fix`, format and check and then commit (it ends `chitty edit -s review` refuses while the worktree has uncommitted files) with: ``format and commit your changes: `chitty edit -s review` runs the configured check and refuses if it fails or the worktree has uncommitted files.`` The current wording is wrapped over lines near line 23 of `work.md` (`git grep -n "refuses while the worktree" -- src/chitty/roles/work.md`); keep the file wrapped as it is. Update `tests/test_guide_work_commits.py` to assert `runs the configured check and refuses if it fails` in place of its assertions on the old wording.

## Acceptance Criteria

- [ ] `tests/test_guide_work_commits.py` asserts `runs the configured check and refuses if it fails` and no longer asserts `then commit your changes` or `refuses while the worktree has uncommitted files`, reading the guide the way it does today; the old sentence is gone from `src/chitty/roles/work.md`; `make check` passes

## History

- 2026-11-22T01:11:08Z lively-zinc-newt → todo
- 2026-11-22T01:11:21Z lively-zinc-newt: changed description, acceptance criteria
