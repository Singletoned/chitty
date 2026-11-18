---
title: Read each ticket from its authoritative ref, not every ref's history
status: planning
depends_on:
  - TASK-377
  - TASK-382
  - TASK-383
parent: TASK-376
created: 2026-11-18
---

## Description

Today `Repo._tasks_in_location` and `Repo.discovered_contexts` in `src/chitty/store.py` read every local and remote-tracking ref's history (`self._history()`, from `git.historical_files`) and take each ticket's copy with the newest commit time, overlaid with this checkout's files. Commit time is not causal order, so this picks wrong copies (`TASK-366`). The decided rule (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`) reads each ticket from one authoritative place, chosen by `ticket_source` (`TASK-377`).

Starts after `TASK-377`, `TASK-382` and `TASK-383` land. The last two stop the runner writing on `main` for tickets with a branch; without them, an error the runner records on `main` would be hidden behind the branch copy.

Decisions:

- Which tickets exist: every ticket file in this checkout's working tree, in `main`'s tip tree, and, for each visible ticket branch, its own ticket file at that branch's tip. A ticket branch is a local branch, or a remote-tracking branch after its first `/`, whose name is `<prefix>-<suffix>` lower-cased for a configured context prefix (`task-5`, `origin/task-5`). A ticket present only on some other branch is not listed.
- For each ticket, call `ticket_source` with: whether this checkout's copy (or, if none, the source copy) has `provisional: true` (`TASK-380`; until it lands, pass `False`), `git.current_branch`, `Repo._main_branch()`, the local and remote-tracking branch tips (`git for-each-ref`, skipping symbolic refs such as `origin/HEAD`), and `contains` backed by `git merge-base --is-ancestor`, called only when a ticket has several candidates. Add the Git helpers to `src/chitty/git.py`.
- `WORKING_TREE`: read this checkout's file, committed or not. A ref: read the file at that ref's tip (`git ls-tree` on the context's active and archive directories, then one `git cat-file --batch` for all blobs, as `git.historical_files` does today). The same ticket in both the active and archive directory of its source stays the existing `used by more than one file` error.
- `StoredTask.branch` is the source ref, or `None` for `WORKING_TREE`, so `show` prints `branch: <ref>` for a ticket read from elsewhere, and `_require_current_version` keeps guarding writes until `TASK-385` replaces it. `StoredTask.path` stays this checkout's path for that file.
- `discovered_contexts` finds directories in the working tree and in `main`'s tip tree, not in history.
- Outside a Git repository every ticket is read from the working tree, as today.
- `next_number` keeps its `_history()` loop until `TASK-379`; `TASK-386` deletes the history code.
- Out of scope: write guards (`TASK-385`), numbering (`TASK-379`), docs (`TASK-387`). Update existing tests that assert the newest-commit choice (likely in `tests/test_store.py`, `tests/test_cli.py`, `tests/test_check_cross_branch_references.py`) to the rule; keep `tests/test_list_performance.py` passing.

Tests: a Hypothesis property with real Git in a new `tests/test_property_ticket_reads.py`, inheriting `RepoTestCase` from `tests/support.py`, with `deadline=None` and a small `max_examples` (about 20) because each example builds a repository. Generate a few tickets, each placed in one of: only on `main`; on `main` and edited on its own local branch; on `main` and edited on a remote-tracking branch only (made with `git update-ref refs/remotes/origin/<branch>`); only on an unrelated branch; and give the branch commits random `GIT_COMMITTER_DATE`s earlier or later than `main`'s. Read from the main checkout and from one ticket's linked worktree. The expected copy is the one `ticket_source` names for the same inputs.

## Acceptance Criteria

- [ ] The property passes: for generated placements, from the main checkout and from a ticket worktree, `Repo.find` and `Repo.tasks` return each listed ticket with the content of the copy `ticket_source` names, and a ticket present only on an unrelated branch is not listed; it fails before the change
- [ ] The `TASK-366` case: a ticket edited on its branch, then edited on `main` with a later `GIT_COMMITTER_DATE`, is read from the branch in the main checkout (`chitty show` prints the branch edit and `branch: task-<n>`); a `todo` ticket whose branch says `doing` lists as `doing` in `chitty list` on `main`; the test fails before the change
- [ ] With only `origin/task-<n>` (no local branch) ahead of `main`, `chitty show` in the main checkout prints its copy; with local `task-<n>` and `origin/task-<n>` diverged, `chitty show` fails naming both
- [ ] With `git.historical_files` patched to raise, `chitty show`, `chitty list` and `chitty check` still work in the main checkout and in a ticket worktree; `make check` passes

## History

- 2026-11-18T16:20:04Z lively-quartz-crane → backlog
- 2026-11-18T16:20:27Z lively-quartz-crane: changed title
- 2026-11-18T16:23:16Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:32:51Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:32:51Z lively-quartz-crane backlog → planning
