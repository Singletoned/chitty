---
title: Check ticket references by ID, so a conflicted ticket does not block edits of others
status: planning
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-21
---

## Description

Split out of `TASK-378` on 2026-11-21. After `TASK-378`, `Repo.lookup` reads each ticket through `source_copy`, which raises for a ticket changed on both its branch and `main` since they split. Reference checks still go through `lookup`: `check.check` (`src/chitty/check.py`, the `depends_on` and `parent` loops, `repo.lookup(dependency) is None` and `repo.lookup(parent) is None`) runs on every autocommitted write through `check.fix`, and `check_dependencies` and the `parent` checks in `add` and `_save` (`src/chitty/store.py`) call `find`. So one conflicted ticket blocks every edit of any ticket that references it.

Rule decided with the owner 2026-11-20: an operation fails only if it needs the conflicted ticket's content. A reference check needs only whether the ID exists.

Decisions:

- A new `Repo.exists(task_id) -> bool`, true exactly when `task_id in self.ticket_ids()`, replaces those two `lookup(...) is None` checks in `check.check`, and the `find` calls that only check a reference exists: `check_dependencies`, and the `parent` checks in `add` and `_save`. Those now raise `no task <ID> in <context directory>` (the `find` message, with `context_of(<ID>)`) when `exists` is false.
- Accepted: `exists` can be true where `find` says `no task`, for example for a ticket only in another checkout's uncommitted files; a reference counts as existing wherever Chitty counts the ID.
- `check.check` otherwise reads only working-tree files and discovers contexts from paths (`TASK-479`), so after this it never reads a referenced ticket's content.

Tests: real Git, in a new `tests/test_reference_isolation.py` with a class inheriting `CliTestCase` from `tests/test_cli.py`, set up as `tests/test_check_cross_branch_references.py` does, with `autocommit = true`. The conflict is made by committing a change to `TASK-1` on `task-1` and a different change to it on `main` after the branch point. No property: a fixed set of references, each in the criteria; `TASK-393` adds the generated property over placements.

## Acceptance Criteria

- [ ] With `autocommit = true`, `TASK-1` edited on both `task-1` and `main` since they split, and `TASK-2` only on `main`: `chitty show TASK-2` succeeds, and `chitty edit TASK-2 --note x` and `chitty note TASK-2 y` succeed and commit; with `TASK-3` committed on `main` with `depends_on: [TASK-1]` and `parent: TASK-1`, `chitty edit TASK-3 --note x` succeeds and commits, and `chitty edit TASK-2 --depends-on TASK-1` succeeds (the `TASK-3` and `--depends-on` cases fail before the change, by the conflict error)
- [ ] `chitty edit TASK-2 --depends-on TASK-99` fails with `no task TASK-99`, and a note records that the `TASK-3` and `--depends-on TASK-1` tests fail with `exists` temporarily written as `return self.lookup(task_id) is not None`
- [ ] With `TASK-1` conflicted as above and `OTHER-1` committed on `main` as the only ticket in an unconfigured `chitty/other/` directory, `chitty show OTHER-1` succeeds; `make check` passes

## History

- 2026-11-21T01:21:49Z quick-pearl-lapwing → planning
