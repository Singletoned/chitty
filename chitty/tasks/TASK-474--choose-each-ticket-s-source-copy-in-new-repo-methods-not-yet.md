---
title: Choose each ticket's source copy in new `Repo` methods, not yet used by reads
status: planning
depends_on:
  - TASK-377
  - TASK-380
  - TASK-396
parent: TASK-376
created: 2026-11-20
---

## Description

On `main`, `Repo._tasks_in_location` and `Repo.discovered_contexts` in `src/chitty/store.py` take each ticket's newest copy across every ref's history (`self._history()`), which picks wrong copies (`TASK-366`). The decided rule (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands: `git show plan/ticket-state:docs/plan/ticket-state.md`) reads each ticket from one place, chosen by `ticket_source` in `src/chitty/ticket_source.py`.

This ticket adds the lookup that applies that rule, as new `Repo` methods, and tests them directly. It changes no existing read or write, and no existing test: `TASK-378` later switches `list`, `show` and writes over to these methods and migrates the old tests. Split out of `TASK-378` so that each step passes `make check`.

New in `src/chitty/store.py`:

- `SourceCopy`, a frozen dataclass: `ref: str | None`, the short name of the ref the copy was read from (`main`, `task-5`, `origin/task-5`; never `refs/heads/...`), or `None` for this checkout's working tree; `path: Path`, the copy's path relative to the repository root; `task: Task`, the parsed copy.
- `Repo.ticket_ids() -> set[TaskId]`: every ticket ID that exists, by the rule below. It reads filenames only, never parses ticket content, and so never raises a parse or source error.
- `Repo.source_copy(task_id: TaskId) -> SourceCopy | None`: the copy to read for that ID, or `None` when its source has no file for it.

Decisions:

- Ticket branches: from `git.branch_tips`, a local branch named a configured context prefix, lower-cased, plus `-<suffix>` (`task-5`), or a remote-tracking branch whose name after its first `/` is one (`origin/task-5`). `task-5-fix` and `plan/ticket-state` are not ticket branches. A remote whose name contains `/` is not supported.
- Which IDs exist: every ticket file in this checkout's working tree, in `main`'s tip, and, for each ticket branch, that branch's own ticket at its tip: the file whose ID, lower-cased, equals the branch's name (`task-5`, or the part after the remote, `origin/task-5`). Other files on a ticket branch, and tickets only on other branches, do not count. Ticket files are recognised as `scan` and `ids.parse_filename` do, in the active and archive directories of any context directory under `chitty/`.
- Choosing the source: on the first `source_copy` call for an ID, call `ticket_source` with: `provisional`, the `provisional` field of the first copy that exists, in this order: this checkout, `main`'s tip, the ticket branch (only that copy is parsed for it); `git.current_branch`; `Repo._main_branch()`; `main_tip` from `git.ref_commit(root, "refs/heads/<main>")`; `local_tips` and `remote_tips`, the ticket branches' tips with `refs/heads/` and `refs/remotes/` stripped; `contains(a, b)` as `git.is_ancestor(root, b, a)`, `False` when `a` is `None`; and `changed_on_both(name)`, true when both `git.changed_since_split(root, ref, main, paths)` and `git.changed_since_split(root, main, ref, paths)` are true, with `ref` and `main` full refs and `paths` the union of this ID's file paths at `main`'s tip and at `ref`'s tip (so an archive on one side and an edit on the other counts). With no `main` commit, `changed_on_both` returns `False` without calling Git.
- Mapping `ticket_source`'s short result to a full ref: `WORKING_TREE` is this checkout; the configured main branch is `refs/heads/<main>`; the ID lower-cased (`task-5`) is `refs/heads/task-5`; anything else is `refs/remotes/<result>`. This is unambiguous because `ticket_source` takes a local candidate only under the exact key `task-5`.
- Reading the source: `WORKING_TREE` reads this checkout's file, committed or not; a file deleted there but not committed is absent. A ref reads the file at that ref's tip. If the source has no file for the ID, `source_copy` returns `None`. More than one file for the ID in the source raises the existing `<ID> is used by more than one file: <paths>` error.
- Errors: `ticket_source`'s errors (diverged refs, changed on both, no `main` tip) and `git.changed_since_split`'s `unrelated histories` error propagate from `source_copy` for that ID only. A copy that fails to parse raises `ChittyError` as `<short ref>:<relative path>: <error>` for a ref, and `<absolute path>: <error>` for the working tree, as `Repo._load` does.
- Caching: the ID list and each ref's files are read once per `Repo`, with one `git.files_at(root, <full ref>, (Path("chitty"),))` call per ref; each ID's chosen copy is cached once chosen. `_invalidate` clears all of it. Never one Git file read per ticket.
- Outside a Git repository: `ticket_ids` is every ticket in the working tree, and `source_copy` reads the working tree (`ref` is `None`).
- Commit `27456731` on branch `task-378` has a first version of this logic (`_build_ticket_index`, `_source_ref`, `_changed_on_both`), wired into reads and choosing every source up front. Reuse its code where it fits; do not wire anything into existing reads.

Tests: real-Git tests in a new `tests/test_ticket_source_copy.py`, inheriting `CliTestCase` from `tests/test_cli.py`, set up as `tests/test_check_cross_branch_references.py` does (`git init`, `git branch -M main`, `autocommit = true`). Tests call `Repo.open(<checkout>).ticket_ids()` and `.source_copy(...)` directly. Make remote-tracking refs with `git update-ref refs/remotes/origin/task-<n> <commit>`; commit `main`'s copy directly with Git where `chitty edit` on `main` would be refused; set `GIT_COMMITTER_DATE` where commit order matters. First add `SourceCopy`, `ticket_ids` and `source_copy` raising `NotImplementedError`, so each test fails on its own. No property: a fixed set of placements, each listed in the criteria and tested; the generated property over placements is `TASK-393`.

## Acceptance Criteria

- [ ] In the main checkout on `main`: a ticket only on `main`, with an uncommitted edit, gives `ref` `None` and the edited task; a ticket edited on `task-<n>` ahead of `main` gives `ref` `task-<n>` and the branch copy, even when a later `main` commit by `GIT_COMMITTER_DATE` touches another ticket; a ticket retitled on `task-<n>` (file renamed there, `main` keeping the old name) appears once in `ticket_ids` and gives the branch path; a ticket only on `origin/task-<n>`, ahead of `main`, gives `ref` `origin/task-<n>`; with local `task-<n>` behind `origin/task-<n>`, it gives `origin/task-<n>`
- [ ] In the main checkout on `main`: a ticket only on branch `feature` is not in `ticket_ids`; a file for `TASK-9` committed only on `task-5` is not in `ticket_ids`; a ticket archived on its branch but active on `main` gives the branch archive path; a ticket whose branch deletes its file gives `None`; a ticket branch fast-forward merged into `main`, followed by a `main` commit changing that ticket, gives `ref` `None` and `main`'s copy
- [ ] In the linked worktree of `task-5`, after a commit there changing `TASK-5`: `TASK-5` gives `ref` `None` and a further uncommitted edit made there; `TASK-7` (no branch) gives `ref` `main` and `main`'s tip copy despite an uncommitted edit to it in that worktree. In a checkout on branch `feature`, an existing ticket gives `ref` `main` despite an uncommitted edit there
- [ ] With local `task-1` and `origin/task-1` diverged, `source_copy(TASK-1)` raises `ChittyError` naming `origin/task-1` and `task-1`; with `TASK-1` edited on both `task-1` and `main` since they split, it names `task-1` and `main`; with `task-1` an orphan branch, it raises the `unrelated histories` error; with a malformed `TASK-1` file committed on `task-1`, it raises `task-1:<relative path>: <error>`. In each case, on the same `Repo`, `ticket_ids()` succeeds and `source_copy(TASK-2)` for a ticket only on `main` succeeds
- [ ] Outside a Git repository, `ticket_ids` lists the working tree tickets and `source_copy` gives `ref` `None`. With `git.historical_files` replaced by a mock that raises, the tests of criteria 1 to 3 still pass. With `git.files_at` wrapped to count calls, `ticket_ids()` followed by `source_copy` for every ID calls it at most once per ref. `make check` passes with no existing test changed (`git diff main --stat -- tests` lists only the new file)

## History

- 2026-11-20T12:35:43Z jolly-dusky-badger → planning
