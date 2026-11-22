---
title: Renumber provisional tickets outside Git
status: cold-read
depends_on:
  - TASK-517
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-517` on 2026-11-22. After `TASK-517`, `Repo.renumber_provisional()` renumbers provisional tickets in a Git repository. This ticket covers a repository outside Git. `TASK-517` landed `renumber_provisional` (rechecked 2026-11-22); add these tests to `tests/test_renumber_provisional.py` as a new `RepoTestCase` class, setting `CHITTY_ACTOR` as `TestPrepareRenumbering` does.

Test in `tests/test_renumber_provisional.py`: in a temporary directory with no `.git`, an up-to-date initialized Chitty repository (`chitty.toml` from `tests/support.py`) with `autocommit = false` and a sole provisional `TASK-AAAAAA` renumbers it to `TASK-1` and creates no `.git`; with `autocommit = true` it raises the usual write-policy error and leaves bytes and paths unchanged.

## Acceptance Criteria

- [ ] Both outside-Git cases pass; `make check` passes

## History

- 2026-11-22T01:35:29Z lively-zinc-newt → planning
- 2026-11-22T03:20:44Z lively-zinc-newt: changed description
- 2026-11-22T03:20:44Z lively-zinc-newt planning → cold-read
