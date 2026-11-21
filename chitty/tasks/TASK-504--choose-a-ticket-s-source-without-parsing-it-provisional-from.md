---
title: "Choose a ticket's source without parsing it: `provisional` from the ID"
status: planning
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

A suffix ID (`TASK-K7Q2MX`) with a file in this working tree or on `main` is provisional. A suffix ID with no file in either place, such as a provisional ticket that exists only on its runner branch `task-k7q2mx`, follows the ticket-branch rules like any other ticket, as it does today. The `provisional: true` field stays as the visible marker. If the field disagrees with the ID, the ID decides. `ticket_source` (`src/chitty/ticket_source.py`), `source_copy`'s own parse of the chosen copy, and every caller are unchanged. No read uses `source_copy` yet (that is `TASK-378`), so `chitty show` does not change.

Measured 2026-11-21 on spike `ab2ac7bf` (branch `spike/task-378`) plus this change: it makes exactly the two tests below fail, and nothing else.

Migrations in `tests/test_source_copy.py`, without weakening any other assertion:

- `test_malformed_working_tree_precedes_main` (line 100): on branch `feature`, numeric `TASK-1` is now read from `main`, so the malformed working-tree copy is not read. Rename it `test_malformed_working_tree_on_another_branch_is_not_read`, and replace the `assertRaises` block with `self.assert_copy(self.source(1), "main", "chitty/tasks/TASK-1--example.md", "original")`.
- `test_provisional_main_and_working_tree_precedence` (line 83): its fixtures mark numeric IDs `provisional: true`. Rename it `test_provisional_is_read_from_the_id`. Use `K7Q2MA` and `K7Q2MC` in place of `1` and `3` (`self.file("K7Q2MA")` works, because `file` formats the number into the path). Then `self.source("K7Q2MA")` is `None`, and `TASK-2` stays `main`'s `original`. `TASK-K7Q2MC`, rewritten on `feature` by `self.file("K7Q2MC", "working")` without the field, is the working-tree copy: `ref` `None`, path `chitty/tasks/TASK-K7Q2MC--example.md`, title `working`. Add numeric `TASK-4` marked `provisional: true` on `main` and deleted on `feature`. It is `main`'s copy (`main`, `chitty/tasks/TASK-4--example.md`, `original`), because the ID decides.

New tests in the same file, using its helpers (`base`, `file`, `commit_at`, `source`, `assert_copy`):

- `test_malformed_working_tree_does_not_stop_a_branch_copy`: `base()`, then on new branch `task-1` `self.file(1, "branch")` committed, `git checkout main`, then overwrite the working-tree `chitty/tasks/TASK-1--example.md` with `not frontmatter\n` (uncommitted). `self.source(1)` is the `task-1` copy titled `branch`, with no error. On `main` today this raises the working-tree parse error.
- `test_provisional_only_on_its_branch_is_read_from_it` (a guard that passes before and after): `init_git()` and commit nothing else. On new branch `task-k7q2mx`, commit `chitty/tasks/TASK-K7Q2MX--example.md` written by `self.file("K7Q2MX")` with `provisional: true` added as in the migration, then `git checkout main`. `self.source("K7Q2MX")` is the `task-k7q2mx` copy titled `original`. It fails for the plausible wrong version `provisional = isinstance(task_id.number, str)` (no file check), which reads the working tree and returns `None`.

Record in a note how each migrated test and the first new test fail on `main` before the change, and that the guard fails against the wrong version above. No property test: these are fixed placements, and the generated property over placements is `TASK-393`.

## History

- 2026-11-21T11:34:10Z sunny-ebony-kestrel → planning
