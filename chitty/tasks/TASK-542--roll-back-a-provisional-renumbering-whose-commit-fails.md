---
title: Roll back a provisional renumbering whose commit fails
status: doing
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

## History

- 2026-11-22T01:35:20Z lively-zinc-newt → planning
- 2026-11-22T03:20:42Z lively-zinc-newt: changed description
- 2026-11-22T03:20:42Z lively-zinc-newt planning → cold-read
- 2026-11-22T03:22:02Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T03:22:02Z lively-zinc-newt cold-read → todo
- 2026-11-22T03:22:13Z lively-zinc-newt: changed description
- 2026-11-22T03:31:35Z vivid-jade-eel todo → doing
