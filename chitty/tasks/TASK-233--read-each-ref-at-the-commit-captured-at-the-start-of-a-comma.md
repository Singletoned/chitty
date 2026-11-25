---
title: Read each ref at the commit captured at the start of a command, so a deleted branch cannot crash ticket discovery
status: done
labels:
  - bug
priority: high
created: 2026-11-09
---

## Description

Observed in Echonomicon (2026-11-09) and here (2026-11-23, `chitty edit TASK-576`): a Chitty command failed with `fatal: Not a valid object name refs/heads/task-...` because another session deleted that branch mid-command. With many runners landing and removing branches, this recurs.

Cause, in `src/chitty/store.py`: `Repo._branch_tips()` and `Repo._main_tip()` capture each ref's commit ID once per command, but two readers then go back to Git by ref name, so a deleted ref fails and a moved ref is read at a different commit:

- `Repo._ref_files` calls `git.files_at(self.root, ref, ...)`.
- `changed_on_both`, inside `Repo._choose_source`, calls `git.changed_since_split(self.root, ref, main_ref, paths)` and the reverse.

Fix: pass the captured commit IDs instead. In `_ref_files`, read each ref at its commit from `_branch_tips()`, and `main` at `_main_tip()`, keeping the ref name as the dictionary key. In `changed_on_both`, pass `tips[ref]` and `main_tip` in place of `ref` and `main_ref`. `tips[ref]` is always present: `ticket_source` only chooses refs drawn from `tips`, and `changed_on_both` returns early when `main_tip` is `None`. Do not change `git.files_at` or `git.changed_since_split` (they accept any commit-ish). Catch no errors and add no fallback to reading by name.

A trial of exactly this fix (2026-11-25) broke only `test_ref_reads_once_and_cached` in `tests/test_ticket_ids.py`, which expects `files_at` to get ref names; change it to expect those refs' commit IDs (`git rev-parse <ref>`). An earlier attempt that changed more than this broke 25 tests, so if many tests fail, compare with the two edits above.

Decided: a command uses the refs captured at its start, so a branch deleted during the command still supplies its tickets to that command; the next command no longer sees it.

Out of scope: `full_ref` mapping, `git.main_files` and `_main_files_for` (`main` is not deleted), `_reject_planning_conflicts` (already reads by commit ID), `src/chitty/run.py`.

Test: a Hypothesis property in a new `tests/test_ref_snapshot.py`, class inheriting `RepoTestCase` from `tests/support.py`, with `examples(...)` from `tests/__init__.py`. Vary a few tickets: whether each is on `main`, whether it has a `task-<n>` branch that changes it or changes something else, whether `main` later changes it too, and what happens to its branch during the command (nothing, deleted, or moved by a new commit). First compute the expected results with a plain `Repo`: `ticket_ids()`, and for each ticket its `source_of`, `source_copy` title, or `ChittyError` text, stored before anything changes (a `Repo` reads lazily). Then patch `git.branch_tips` (`unittest.mock.patch.object`) with a function that calls the original, saved before patching, and on its first call only applies the deletions (`git update-ref -d refs/heads/task-<n>`, since `git branch -D` refuses a branch checked out elsewhere) and moves before returning. Property: a new `Repo` under that patch gives the expected results. (`_reject_planning_conflicts` calls `git.branch_tips` uncached and sees the changed refs; that does not affect these results.) Add `@example`s covering a deleted branch-only ticket, a moved branch, and a ticket changed on both `main` and a deleted branch (this one reaches `changed_since_split`).

## Acceptance Criteria

- [x] The property in `tests/test_ref_snapshot.py`, with its `@example`s, passes, and fails with the `store.py` fix reverted
- [x] Regression tests: `test_ref_reads_once_and_cached` expects commit IDs and passes; `make check` passes

## Plan

Capture expected ticket discovery before mutating refs, add a property test proving snapshot consistency, then read files and split changes using captured commit IDs. Update the caching regression test, run formatting and checks, and hand off for review.

## Notes

The new snapshot property fails before the fix: deleted refs cause git ls-tree to fail, and moved refs return the new title instead of the captured title.

With only the split-change fix reverted, the deleted conflicting branch example also fails at git merge-base; restoring it passes.

Reviewed: Snapshot reads use captured commit IDs; the property detects the original race.
1: pass - `make check` passes the property and its explicit examples. In a temporary merge-base worktree with the new test and `PYTHONPATH` pointing to its `src`, `TEST_TIER=check python -m pytest -q tests/test_ref_snapshot.py --tb=short` fails: deleted refs produce `fatal: Not a valid object name`, and moved refs yield `moved` instead of `branch`.
2: pass - `test_ref_reads_once_and_cached` expects `git rev-parse` commit IDs; `make check` passed (1190 tests, 621 subtests).

## Summary

Ticket discovery and conflict selection read captured commit IDs, preserving the command snapshot when branches move or disappear. Added a real-Git snapshot property with deletion, movement and conflicting-change examples; verified failures before the fix and with the split-change fix independently reverted. Updated the caching regression. make check passed.

## History

- 2026-11-09T12:03:06Z eager-puffin → backlog
- 2026-11-09T12:03:08Z eager-puffin: changed notes
- 2026-11-09T12:04:53Z eager-puffin: changed labels, priority, parent, acceptance criteria, notes
- 2026-11-09T12:07:50Z eager-puffin: changed acceptance criteria, notes
- 2026-11-11T10:18:05Z vivid-yellowhammer: changed parent
- 2026-11-24T07:46:55Z kind-navy-toad: changed title, description, acceptance criteria
- 2026-11-24T07:46:55Z kind-navy-toad backlog → planning
- 2026-11-24T07:47:06Z kind-navy-toad: replaced notes
- 2026-11-24T07:47:07Z kind-navy-toad planning → cold-read
- 2026-11-24T07:48:07Z kind-navy-toad: changed description
- 2026-11-24T07:48:07Z kind-navy-toad cold-read → planning
- 2026-11-24T07:52:34Z kind-navy-toad: changed description
- 2026-11-24T07:52:43Z kind-navy-toad planning → cold-read
- 2026-11-24T07:54:33Z kind-navy-toad: changed description
- 2026-11-24T07:54:33Z kind-navy-toad cold-read → todo
- 2026-11-24T08:33:54Z intrepid-umber-quail todo → doing
- 2026-11-24T08:36:23Z intrepid-umber-quail: wrote the plan
- 2026-11-24T08:39:47Z intrepid-umber-quail: changed owner, notes
- 2026-11-24T08:39:47Z intrepid-umber-quail doing → planning
- 2026-11-25T20:44:32Z golden-coral-stoat: changed notes
- 2026-11-25T21:15:32Z daring-ebony-wren: replaced notes; changed owner, description, acceptance criteria; wrote the plan
- 2026-11-25T21:15:32Z daring-ebony-wren planning → cold-read
- 2026-11-25T21:19:25Z daring-ebony-wren: changed description, acceptance criteria
- 2026-11-25T21:19:25Z daring-ebony-wren cold-read → planning
- 2026-11-25T21:19:46Z daring-ebony-wren planning → todo
- 2026-11-25T21:24:56Z honest-zinc-vole todo → doing
- 2026-11-25T21:28:42Z honest-zinc-vole: wrote the plan
- 2026-11-25T21:29:32Z honest-zinc-vole: changed notes
- 2026-11-25T21:33:45Z honest-zinc-vole: changed notes
- 2026-11-25T21:33:52Z honest-zinc-vole: changed summary
- 2026-11-25T21:36:09Z honest-zinc-vole doing → review
- 2026-11-25T21:42:21Z eager-zinc-wren: changed notes; ticked acceptance criteria
- 2026-11-25T21:42:21Z eager-zinc-wren review → done
