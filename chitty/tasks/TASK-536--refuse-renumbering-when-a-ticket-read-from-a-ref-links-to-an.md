---
title: Refuse renumbering when a ticket read from a ref links to an old ID
status: planning
depends_on:
  - TASK-519
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-519` on 2026-11-22 (the worker model gave up twice on the combined ticket). After `TASK-519`, `Repo._plan_provisional_renumbering` (`src/chitty/store.py`) refuses a plan when an untouched on-disk ticket links to a renumbered ID. This ticket extends the same guard to ticket copies read from refs. Draft: keep in planning until `TASK-519` lands, then check its landed helper and cold-read.

- After the disk scan, check every ID in `ticket_ids()` whose `source_of(id)` is not `None`: read it with `self.lookup(id)`, skipping a `None` result, and apply `blocking_link(frontmatter, mapping)` (`src/chitty/renumbering.py`). This covers IDs with no disk file and stale disk copies whose branch copy adds the link. Visit them in `sorted(...)` `TaskId` order, after every disk file; raise the same message as `TASK-519` on the first block (`cannot renumber {old}: {blocking} links to it in {field}`). Source-selection and read errors propagate.
- Read ref-backed tickets only through `lookup`, which applies the source policy (`_choose_source`); this ticket adds no tests for refs it does not select.

Tests: extend `tests/test_provisional_link_guard.py` (from `TASK-519`), with its snapshot helper and eligible candidate `TASK-AAAAAA`:

- (c) a `TASK-3` that exists only on branch `task-3` (committed there, absent from `main` and the working tree), with `depends_on: [TASK-AAAAAA]`. Assert `source_of(TASK-3) == "task-3"`. Expected message: `cannot renumber TASK-AAAAAA: TASK-3 links to it in depends_on`.
- (e) `TASK-3` committed on `main` with no `parent`, then branch `task-3` adds `parent: task-aaaaaa`. Assert `source_of(TASK-3) == "task-3"`. Expected message: `cannot renumber TASK-AAAAAA: TASK-3 links to it in parent`.
- Prose variant of (c): `See TASK-AAAAAA.` in the branch copy's Description instead of the link; the plan returns `{TASK-AAAAAA: TASK-4}` (the branch-only `TASK-3` reserves 3).

A cold reader's probe (2026-11-21) on the unguarded planner: (c) and (e) give `source_of(TASK-3) == "task-3"` and mapping `{TASK-AAAAAA: TASK-4}` with no error, so both refusal tests fail today.

## Acceptance Criteria

- [ ] Fixtures (c) and (e) raise `ChittyError` whose `str()` equals the expected message, with HEAD, index and snapshotted bytes unchanged, and each fails before this change; the (c) prose variant returns `{TASK-AAAAAA: TASK-4}`; `make check` passes

## History

- 2026-11-22T00:16:22Z lively-zinc-newt → planning
