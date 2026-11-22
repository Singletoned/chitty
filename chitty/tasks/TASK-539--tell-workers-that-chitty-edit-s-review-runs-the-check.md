---
title: Tell workers that `chitty edit -s review` runs the check
status: todo
depends_on:
  - TASK-538
created: 2026-11-22
---

## Description

Replaces the second half of `TASK-343`. After `TASK-538`, `chitty edit -s review` runs the configured check itself, so the work guide need not tell workers to run it.

In `src/chitty/roles/work.md`, replace the sentence that tells workers to run `chitty fix`, format and check and then commit (it ends `chitty edit -s review` refuses while the worktree has uncommitted files) with: ``format and commit your changes: `chitty edit -s review` runs the configured check and refuses if it fails or the worktree has uncommitted files.`` Find the exact current wording with `git grep -n "refuses while the worktree" -- src/chitty/roles/work.md` before editing. Update `tests/test_guide_work_commits.py` to assert `runs the configured check and refuses if it fails` in place of its assertions on the old wording.

## Acceptance Criteria

- [ ] `git grep -n "runs the configured check and refuses if it fails" -- src/chitty/roles/work.md` finds the new sentence, the old sentence is gone, and `tests/test_guide_work_commits.py` asserts the new wording; `make check` passes

## History

- 2026-11-22T01:11:08Z lively-zinc-newt → todo
