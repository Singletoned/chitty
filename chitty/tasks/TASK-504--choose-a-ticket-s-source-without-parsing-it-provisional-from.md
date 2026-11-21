---
title: "Choose a ticket's source without parsing it: `provisional` from the ID"
status: doing
priority: high
parent: TASK-376
created: 2026-11-21
---

## Description

Split from `TASK-378` on 2026-11-21, because three workers found that ticket too large for one session. This piece lands first and alone.

On `main`, `Repo._choose_source` in `src/chitty/store.py` (about lines 522-528) parses the working-tree copy of a ticket, or `main`'s copy when there is none, only to learn its `provisional:` field before calling `ticket_source`. So `Repo.source_copy` raises on a malformed working-tree or `main` copy even when the copy it should choose is a valid one on a ticket branch. `TASK-378` needs `context_of` never to parse, and this parse prevents that.

Decided with the owner 2026-11-21 (recorded in `docs/plan/ticket-state.md` on branch `plan/ticket-state`): choosing the source parses nothing. Replace the lines from `copies = self._working_ticket_files(task_id)` to `provisional = first is not None and first.task.frontmatter.provisional is True` with

```python
provisional = isinstance(task_id.number, str) and bool(
    self._working_ticket_files(task_id) or self._ref_ticket_files(main_ref, task_id)
)
```

A suffix ID (`TASK-K7Q2MX`) with a file in this working tree or on `main` is provisional. A suffix ID with no file in either place, such as a provisional ticket that exists only on its runner branch `task-k7q2mx`, follows the ticket-branch rules like any other ticket, as it does today. The `provisional: true` field stays as the visible marker. If the field disagrees with the ID, the ID decides: a suffix ID with a file here or on `main` is read from the working tree even when its `provisional` field is false or absent, and its `task-<id>` branch copy is then ignored. Real provisional tickets always carry the field, so for them nothing changes. `ticket_source` (`src/chitty/ticket_source.py`), `source_copy`'s own parse of the chosen copy, and every caller are unchanged. No read uses `source_copy` yet (that is `TASK-378`), so `chitty show` does not change.

Measured 2026-11-21 on spike `ab2ac7bf` (branch `spike/task-378`) plus this change: it makes exactly the two tests below fail, and nothing else.

Migrations in `tests/test_source_copy.py`, without weakening any other assertion:

- `test_malformed_working_tree_precedes_main` (line 100): on branch `feature`, numeric `TASK-1` is now read from `main`, so the malformed working-tree copy is not read. Rename it `test_malformed_working_tree_on_another_branch_is_not_read`, and replace the `assertRaises` block with `self.assert_copy(self.source(1), "main", "chitty/tasks/TASK-1--example.md", "original")`. Remove the import `from chitty.errors import ChittyError` (line 6), which nothing else in the file uses, or ruff fails.
- `test_provisional_main_and_working_tree_precedence` (line 83): its fixtures mark numeric IDs `provisional: true`. Rename it `test_provisional_is_read_from_the_id`. In the fixture loop, use `for number in ("K7Q2MA", "K7Q2MC", 4):` in place of `(1, 3)`, so all three are committed on `main` with `provisional: true` (`file` formats the number into the path). Keep `self.file(2)`, committed on `main` without the field. On `feature`, unlink `TASK-K7Q2MA--example.md`, `TASK-2--example.md` and `TASK-4--example.md`, and rewrite `TASK-K7Q2MC` with `self.file("K7Q2MC", "working")`, which drops the field. Then: `self.source("K7Q2MA")` is `None`, because the suffix ID with a file on `main` is read from the working tree, where it is gone; `TASK-2` stays `main`'s `original`; `TASK-K7Q2MC` is the working-tree copy (`ref` `None`, path `chitty/tasks/TASK-K7Q2MC--example.md`, title `working`); and numeric `TASK-4` is `main`'s copy (`main`, `chitty/tasks/TASK-4--example.md`, `original`), because the ID decides.

New tests in the same file, using its helpers (`base`, `file`, `commit_at`, `source`, `assert_copy`):

- `test_malformed_working_tree_does_not_stop_a_branch_copy`: `base()`, then on new branch `task-1` `self.file(1, "branch")` committed, `git checkout main`, then overwrite the working-tree `chitty/tasks/TASK-1--example.md` with `not frontmatter\n` (uncommitted). `self.source(1)` is the `task-1` copy titled `branch`, with no error. On `main` today this raises the working-tree parse error.
- `test_provisional_only_on_its_branch_is_read_from_it` (a guard that passes before and after): `init_git()` and commit nothing else. On new branch `task-k7q2mx`, commit `chitty/tasks/TASK-K7Q2MX--example.md` written by `self.file("K7Q2MX")` and then given the field by replacing `status: todo` with `provisional: true\nstatus: todo`, as the precedence test does (lines 86-89), then `git checkout main`. `self.source("K7Q2MX")` is the `task-k7q2mx` copy titled `original`. It fails for the plausible wrong version `provisional = isinstance(task_id.number, str)` (no file check), which reads the working tree and returns `None`.

Record in a note how each migrated test and the first new test fail on `main` before the change, and that the guard fails against the wrong version above. No property test: these are fixed placements, and the generated property over placements is `TASK-393`.

## Acceptance Criteria

- [ ] The two migrated tests and `test_malformed_working_tree_does_not_stop_a_branch_copy` in `tests/test_source_copy.py` pass, and each fails on `main` before the change (recorded in a note)
- [ ] `test_provisional_only_on_its_branch_is_read_from_it` passes before and after the change, and fails against `provisional = isinstance(task_id.number, str)` without the file check (recorded in a note)
- [ ] `make check` passes, and `git diff main -- src` changes only `_choose_source` in `src/chitty/store.py`

## Plan

Migrate and add the specified source-copy tests, verify their baseline failures and guard behavior, then replace provisional detection with the specified ID and file-presence check. Run formatting and checks, verify the source diff, and hand off.

## Notes

Baseline against unchanged source: test_provisional_is_read_from_the_id failed because the fieldless working copy resolved to main; test_malformed_working_tree_on_another_branch_is_not_read errored on unclosed frontmatter; test_malformed_working_tree_does_not_stop_a_branch_copy errored on missing frontmatter. The branch-only provisional guard passed on baseline and failed with an unexpectedly None copy when provisional was determined solely by isinstance(task_id.number, str).

## History

- 2026-11-21T11:34:10Z sunny-ebony-kestrel → planning
- 2026-11-21T11:34:26Z sunny-ebony-kestrel: changed acceptance criteria
- 2026-11-21T11:34:42Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T11:35:50Z sunny-ebony-kestrel: changed description
- 2026-11-21T11:37:07Z sunny-ebony-kestrel: changed description
- 2026-11-21T11:37:07Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T11:37:36Z vivid-quartz-badger todo → doing
- 2026-11-21T11:39:36Z vivid-quartz-badger: wrote the plan
- 2026-11-21T11:40:19Z vivid-quartz-badger: changed notes
