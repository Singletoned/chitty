---
title: Refuse renumbering when a ticket read from a ref links to an old ID
status: doing
depends_on:
  - TASK-519
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-519` on 2026-11-22 (the worker model gave up twice on the combined ticket). After `TASK-519`, `Repo._plan_provisional_renumbering` (`src/chitty/store.py`) refuses a plan when an untouched on-disk ticket links to a renumbered ID. This ticket extends the same guard to ticket copies read from refs. `TASK-519` landed `Repo._guard_untouched_disk_links(entries, writable, mapping)` in `src/chitty/store.py`, called right after `plan_renumbering` in `_plan_provisional_renumbering` (rechecked on `main` 2026-11-22). Add a sibling method `_guard_ref_links(mapping: dict[TaskId, TaskId]) -> None` and call it on the next line. Its tests go in `TestProvisionalLinkGuard` in `tests/test_provisional_link_guard.py` (which inherits `TestProvisionalPreflight` and has `fixture`, `state`, `check_refusal` and `check_success` helpers); reuse or extend those helpers.

- After the disk scan, check every ID in `ticket_ids()` whose `source_of(id)` is not `None`: read it with `self.lookup(id)`, skipping a `None` result, and apply `blocking_link(frontmatter, mapping)` (`src/chitty/renumbering.py`). This covers IDs with no disk file and stale disk copies whose branch copy adds the link. Visit them in `sorted(...)` `TaskId` order, after every disk file; raise the same message as `TASK-519` on the first block (`cannot renumber {old}: {blocking} links to it in {field}`). Source-selection and read errors propagate.
- Read ref-backed tickets only through `lookup`, which applies the source policy (`_choose_source`); this ticket adds no tests for refs it does not select.

Tests: add to `TestProvisionalLinkGuard` in `tests/test_provisional_link_guard.py` a new helper `ref_fixture(self, case: str) -> None`, using the class's `init_git`, `file`, `commit` and `git` helpers (the existing `fixture` cannot build these):

1. `self.init_git()`; `self.file("tasks", "TASK-AAAAAA", provisional=True)`; `self.commit()`.
2. `case == "branch-only"` or `"branch-only-prose"`: `self.git("switch", "-c", "task-3")`; `path = self.file("tasks", "TASK-3")`; for `"branch-only"` insert `depends_on: [TASK-AAAAAA]` after the `status: todo` line, for `"branch-only-prose"` append `See TASK-AAAAAA.` to the file; `self.commit()`; `self.git("switch", "main")` (the file then exists only on `task-3`).
3. `case == "branch-adds"`: `path = self.file("tasks", "TASK-3")`; `self.commit()`; `self.git("switch", "-c", "task-3")`; insert `parent: task-aaaaaa` after the `status: todo` line; `self.commit()`; `self.git("switch", "main")`.
4. Finally assert `Repo.open(self.root).source_of(TaskId.parse("TASK-3")) == "task-3"`.

Tests, each in its own repository: `test_branch_only_link` (`"branch-only"`) and `test_branch_adds_link` (`"branch-adds"`) take `self.state()`, call the planner, assert `str()` of the `ChittyError` equals `cannot renumber TASK-AAAAAA: TASK-3 links to it in depends_on` and `... in parent` respectively, and that `self.state()` is unchanged. `test_branch_only_prose` (`"branch-only-prose"`) asserts the mapping is `{TASK-AAAAAA: TASK-4}` and the state is unchanged.

Not tested, by decision: the scan order (each fixture has one blocking link) and skipping a `None` from `lookup` (no simple fixture produces it).

A cold reader's probe (2026-11-21) on the unguarded planner: (c) and (e) give `source_of(TASK-3) == "task-3"` and mapping `{TASK-AAAAAA: TASK-4}` with no error, so both refusal tests fail today.

## Acceptance Criteria

- [ ] `test_branch_only_link` and `test_branch_adds_link` pass, and each fails before this change (record the failing run in a note)
- [ ] `test_branch_only_prose` passes, and the existing tests in `tests/test_provisional_link_guard.py` still pass; `make check` passes

## Plan

Add ref-backed fixtures and demonstrate both refusal regressions, then scan selected ref tickets after the disk guard and run the full checks.

## History

- 2026-11-22T00:16:22Z lively-zinc-newt → planning
- 2026-11-22T00:33:44Z lively-zinc-newt: changed description
- 2026-11-22T00:33:44Z lively-zinc-newt planning → cold-read
- 2026-11-22T00:34:56Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T00:34:56Z lively-zinc-newt cold-read → todo
- 2026-11-22T01:19:40Z eager-jade-heron todo → doing
- 2026-11-22T01:21:41Z eager-jade-heron: wrote the plan
