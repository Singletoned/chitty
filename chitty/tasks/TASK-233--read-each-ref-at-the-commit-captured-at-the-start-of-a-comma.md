---
title: Read each ref at the commit captured at the start of a command, so a deleted branch cannot crash ticket discovery
status: planning
labels:
  - bug
priority: high
created: 2026-11-09
---

## Description

Observed in Echonomicon on 2026-11-09 (Chitty `0.1.43`): `chitty list` failed with `fatal: bad revision 'refs/heads/task-90'` while branch cleanup deleted `task-90`; a retry succeeded. The person: branch cleanup must not make `chitty list` blow up.

The code has changed since then (`historical_files` is gone), but the race remains. Probed on `main` at `02ece9f1` (2026-11-24): with `task-1` deleted right after `git.branch_tips` returns, `Repo.ticket_ids()`, `Repo.all_tasks()` and `Repo.find()` each raise `` `git ls-tree -r -z --full-tree refs/heads/task-1 -- chitty` failed ... fatal: Not a valid object name refs/heads/task-1 ``.

Cause, in `src/chitty/store.py`: `Repo._branch_tips()` captures every ref with its commit ID once per command (`git.branch_tips`, cached in `_branch_tips_value`), and `Repo._main_tip()` captures `main`'s. But two readers then go back to Git by ref name:

- `Repo._ref_files` calls `git.files_at(self.root, ref, ...)` with the ref name.
- `changed_on_both` inside `Repo._choose_source` calls `git.changed_since_split(self.root, ref, main_ref, paths)` (and the reverse) with ref names.

A deleted ref makes these fail, and a ref that moved makes them read a different commit than the one `ticket_source` compared with `contains` (which already uses the captured commit IDs).

Fix: pass the captured commit IDs instead. In `_ref_files`, read each ref at its commit from `_branch_tips()`, and `main` at `_main_tip()`, keeping the ref name as the dictionary key (callers and messages use it). In `changed_on_both`, pass `tips[full_ref(name)]` and `main_tip` to `git.changed_since_split` in place of `ref` and `main_ref`. `git.files_at` and `git.changed_since_split` already accept any commit-ish; do not change them. Catch no errors: a Git failure still raises, including a captured commit pruned by `git gc` during the command; add no fallback to reading by name. Remote-tracking refs (`refs/remotes/...`) are in `_branch_tips()` too and are read the same way.

Decided: one command uses the refs captured at its start, so a branch deleted during the command still supplies its tickets to that command; the next command no longer sees it.

`tests/test_ticket_ids.py` `test_ref_reads_once_and_cached` asserts that `files_at` gets ref names; change its expected values to those refs' commit IDs (`git rev-parse <ref>`).

Out of scope: how `full_ref` in `_choose_source` maps names (unchanged); `git.main_files` and `_main_files_for` (read `main` by name; `main` is not deleted by cleanup); `_reject_planning_conflicts` (already reads fresh tips by commit ID); `src/chitty/run.py`. `TASK-598` changes other parts of `store.py` on its branch; neither depends on the other.

Test: a Hypothesis property in a new `tests/test_ref_snapshot.py`, class inheriting `RepoTestCase` from `tests/support.py`, with `@settings(max_examples=examples(20))` (`examples` from `tests/__init__.py`). Each example builds a fresh repository under `self.root / "example"` (remove it first; write `CONFIG` from `tests/support.py` as its `chitty.toml`; `git init`, user name and email, `git branch -M main`). It draws three tickets, `TASK-1` to `TASK-3`, each with:

- `on_main`: boolean; when true, its file (`chitty/tasks/TASK-<n>--example.md`, title `main`, status `todo`, created `2026-01-01`) is in the first commit on `main`;
- `branch`: `none`, `changes` (branch `task-<n>` from `main` with one commit writing the ticket file with title `branch`) or `unrelated` (branch `task-<n>` with one commit changing only a non-ticket file);
- `main_changes`: boolean; when true, after the branches exist, `main` gets a commit writing the ticket file with title `main later`;
- `race`: `none`, `delete` (`git branch -D task-<n>`) or `move` (a new commit on `task-<n>` writing the ticket file with title `moved`), ignored when `branch` is `none`.

Outcome of a `Repo`: `sorted(map(str, repo.ticket_ids()))`, and for each ticket either `None` (no copy), `(repo.source_of(id), copy.task.frontmatter.title)` where `copy = repo.source_copy(id)`, or the text of the `ChittyError` it raises. The property: open a `Repo`, record its outcome (the expected value); then open a new `Repo` with `git.branch_tips` patched (`unittest.mock.patch.object`) to call the real function and then, on its first call only, apply every ticket's `race`; its outcome equals the expected value. Then a third `Repo` returns an outcome without raising, and for each ticket with `on_main` and `main_changes` false, `branch` `changes` and `race` `delete`, its ID is not in that third `Repo`'s `ticket_ids()`.

Add `@example`s so `make check` always covers: one branch-only ticket (`on_main` false, `changes`) deleted; one `changes` branch moved; one ticket with `on_main`, `changes`, `main_changes` and `delete` (it reaches `changed_since_split`). Others `on_main` false, `branch` `none`.

Probed while planning with this exact recipe: it fails on `main`; it passes with the fix (100 examples under `TEST_TIER=thorough`, about 2 s under `check`); it fails against two wrong fixes: (A) `_ref_files` still calls `git.files_at` with the ref name, but wraps each call in `try`/`except ChittyError` and leaves that ref out of `_ticket_ref_files`, with `changed_on_both` as on `main`; (C) `_ref_files` fixed as above, but `changed_on_both` still passes `ref` and `main_ref`. Re-run the test once against each of A and C and against `main`, without committing them, and record the results in a note.

## Acceptance Criteria

- [ ] The property in `tests/test_ref_snapshot.py` (with its three `@example`s) passes, and fails on `main` and against wrong fixes A and C; a note records the four runs
- [ ] `tests/test_ticket_ids.py` `test_ref_reads_once_and_cached` expects commit IDs and passes; `make check` passes

## Plan

Implement captured-commit-ID reads in store.py, add the specified snapshot property, and update the existing expectation. Establish regression failures on current code and wrong fixes A/C, verify corrected behavior, run make check, and record results.

## Notes

Suggestion origin: echonomicon. Distinct from completed `TASK-164`, which surfaced Git errors instead of discarding tickets; this ticket keeps that and only stops reading refs by name after capturing them.

Implementation investigation found a conflict between the stated snapshot design and existing conflict detection: using captured commits in changed_since_split altered merge-base/change detection and caused 25 make check failures (including test_changed_both and provisional conflict tests). Existing relevant code is Repo._choose_source.changed_on_both; make check reproduces failures. Decision needed: specify the intended changed_since_split semantics with captured IDs while preserving current conflict behavior, or revise the required design/acceptance criteria. No test/property work completed; partial store.py change is uncommitted and should be preserved or reverted during planning.

Folded in from TASK-671 (2026-11-25): on 2026-11-23, `chitty edit TASK-576 ...` in `.worktrees/task-576` failed with `git ls-tree -r -z --full-tree refs/heads/task-yj6vbs -- chitty` ... `fatal: Not a valid object name refs/heads/task-yj6vbs`, because another session deleted branch `task-yj6vbs` between Chitty listing branches and reading them. Rerunning succeeded. With many runners landing and removing branches, this race recurs.

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
