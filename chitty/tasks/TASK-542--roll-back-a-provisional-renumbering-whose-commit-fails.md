---
title: Roll back a provisional renumbering whose commit fails
status: review
depends_on:
  - TASK-517
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-517` on 2026-11-22. After `TASK-517`, `Repo.renumber_provisional()` in `src/chitty/store.py` writes every changed ticket and makes one commit inside `_all_or_nothing`. This ticket proves a failed commit leaves nothing behind. `TASK-517` landed `renumber_provisional` and `test_transaction` in `TestPrepareRenumbering` (`tests/test_renumber_provisional.py`), whose `fixture()` builds the batch; add this test to that class (rechecked 2026-11-22).

Test in `tests/test_renumber_provisional.py`: build `TASK-517`'s batch fixture, install an executable `.git/hooks/pre-commit` that exits 1, then snapshot ticket bytes and paths, HEAD, the index (`git ls-files -s`) and `git status --porcelain`, call `renumber_provisional()`, and assert the `ChittyError` contains `autocommit failed` and every snapshot item is unchanged. A cold reader's probe (2026-11-22) found today's rollback (`_all_or_nothing`, `_restore_task_files` in `src/chitty/store.py`) already restores everything, so this is a regression test of landed behaviour; add it anyway. Evidence: run it with `_restore_task_files` replaced by a no-op (`mock.patch("chitty.store._restore_task_files")`; it is a module-level function), confirm it fails, and record that in a note.

## Acceptance Criteria

- [ ] The failing-hook test passes; a note records it failing with `_restore_task_files` disabled; `make check` passes

## Plan

Add a failing pre-commit hook regression test using the existing batch fixture, verify it detects disabled restoration, then run the full checks and commit.

## Notes

With restoration patched to a no-op, the new test fails on the snapshot comparison: renumbered ticket paths and contents remain after the hook rejects the commit.

## Summary

Added a failing-hook rollback regression test; verified it fails when restoration is disabled and passes normally. make check passes.

## History

- 2026-11-22T01:35:20Z lively-zinc-newt → planning
- 2026-11-22T03:20:42Z lively-zinc-newt: changed description
- 2026-11-22T03:20:42Z lively-zinc-newt planning → cold-read
- 2026-11-22T03:22:02Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T03:22:02Z lively-zinc-newt cold-read → todo
- 2026-11-22T03:22:13Z lively-zinc-newt: changed description
- 2026-11-22T03:31:35Z vivid-jade-eel todo → doing
- 2026-11-22T03:33:59Z vivid-jade-eel: wrote the plan
- 2026-11-22T03:34:24Z vivid-jade-eel: changed notes
- 2026-11-22T03:37:02Z vivid-jade-eel: changed summary
- 2026-11-22T03:39:23Z vivid-jade-eel doing → review
