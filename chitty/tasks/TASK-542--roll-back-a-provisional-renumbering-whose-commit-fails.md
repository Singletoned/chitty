---
title: Roll back a provisional renumbering whose commit fails
status: planning
depends_on:
  - TASK-517
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-517` on 2026-11-22. After `TASK-517`, `Repo.renumber_provisional()` in `src/chitty/store.py` writes every changed ticket and makes one commit inside `_all_or_nothing`. This ticket proves a failed commit leaves nothing behind. Draft: keep in planning until `TASK-517` lands, then reuse its fixture and cold-read.

Test in `tests/test_renumber_provisional.py`: build `TASK-517`'s batch fixture, install an executable `.git/hooks/pre-commit` that exits 1, snapshot ticket bytes and paths, HEAD, the index (`git ls-files -s`) and `git status --porcelain`, call `renumber_provisional()`, and assert the `ChittyError` contains `autocommit failed` and every snapshot item is unchanged. If the existing rollback does not restore everything, fix it here and keep this test.

## Acceptance Criteria

- [ ] The failing-hook test passes; `make check` passes

## History

- 2026-11-22T01:35:20Z lively-zinc-newt → planning
