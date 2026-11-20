---
title: List which ticket IDs exist across the working tree, `main` and ticket branches
status: doing
depends_on:
  - TASK-377
  - TASK-380
  - TASK-396
parent: TASK-376
created: 2026-11-20
---

## Description

On `main`, `Repo._tasks_in_location` and `Repo.discovered_contexts` in `src/chitty/store.py` take each ticket's newest copy across every ref's history (`self._history()`), which picks wrong copies (`TASK-366`). The decided rule (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands: `git show plan/ticket-state:docs/plan/ticket-state.md`) reads each ticket from one place, chosen by `ticket_source` in `src/chitty/ticket_source.py`.

This is the first of four tickets that build that lookup as new `Repo` methods, unused by existing reads: this one lists which ticket IDs exist; `TASK-476` adds `Repo.source_copy`, choosing and reading each ticket's copy; `TASK-477` and `TASK-478` test it from other checkouts and for errors. `TASK-378` then switches reads over. This ticket changes no existing read, write or test.

New in `src/chitty/store.py`: `Repo.ticket_ids() -> set[TaskId]`, every ticket ID that exists, by the rule below. It parses no ticket content.

Decisions:

- Ticket branches: from `git.branch_tips` (full ref names), a local branch whose name after `refs/heads/`, upper-cased, `TaskId.parse` accepts with a configured context prefix and whose name equals that ID lower-cased (`task-5`), or a remote-tracking branch whose name after `refs/remotes/` and its first `/` is one (`origin/task-5`). `task-5-fix` and `plan/ticket-state` are not ticket branches. Branches of a remote whose name contains `/` are silently not ticket branches.
- Which IDs exist: every ticket file in this checkout's working tree, at `main`'s tip, and, for each ticket branch, that branch's own ticket at its tip: the file whose ID, lower-cased, equals the branch's name (`task-5`, or the part after the remote). Other files on a ticket branch, and tickets only on other branches, do not count. A ticket deleted on its branch but present on `main` stays listed.
- Ticket files are the entries `scan` (`src/chitty/store.py`) finds with `allow_any_prefix=True`, as `Repo._files` calls it: files directly in `chitty/<dir>/` or `chitty/<dir>/archive/`, for every directory `<dir>` under `chitty/` in that tree. In the working tree, list `chitty/<dir>` directories from the filesystem; do not call `discovered_contexts`, which reads history. In a ref's files from `git.files_at`, an entry is a blob at exactly `chitty/<dir>/<name>` or `chitty/<dir>/archive/<name>`; deeper paths are ignored. In the working tree and at `main`'s tip, an entry `scan` would report a problem for raises `ChittyError`: `<path>: <problem>` for the working tree, as `Repo._files` does, and `main:<relative path>: <problem>` for `main`. On a ticket branch only its own ticket file is looked for; other entries there are ignored.
- When the configured main branch (`Repo._main_branch()`) has no commit (`git.ref_commit(root, "refs/heads/<main>")` is `None`), `main` contributes no files and `ticket_ids` does not fail.
- Reading refs: one `git.files_at(root, <full ref>, (Path("chitty"),))` call per ref, `main` included (not `git.main_files` or `Repo._main_files_for`), cached per `Repo` with the ID list so `TASK-476` can reuse the files; `_invalidate` clears the cache. Never one Git file read per ticket.
- Outside a Git repository (`git.is_repository(root)` is false), call no other `chitty.git` function: `ticket_ids` is every ticket in the working tree.
- Commit `bed36801` on branch `task-378` (originally `27456731`, reverted there by `0ac2ee94`) has a first version of this logic in `_build_ticket_index`; reuse its code where it fits.

Recording `chitty.git` calls, wherever a criterion asks for it: wrap each public function in `chitty.git` and record only outermost calls; a call made while another wrapped `chitty.git` function is running (such as the helper `git.is_repository` calls itself) is not recorded.

Tests: real-Git tests in a new `tests/test_ticket_ids.py`, inheriting `CliTestCase` from `tests/test_cli.py`, set up as `tests/test_check_cross_branch_references.py` does (`git init`, `git branch -M main`, `autocommit = true`), one test per case in the criteria, calling `Repo.open(<checkout>).ticket_ids()` directly. For the no-commit case, set `main_branch = "trunk"` in `chitty.toml` with no `refs/heads/trunk`. Make remote-tracking refs with `git update-ref refs/remotes/origin/task-<n> <commit>`; commit with Git directly where `chitty` would refuse. Before implementing, write `ticket_ids` raising `NotImplementedError` and run the new tests, so each fails on its own. No property: a fixed set of cases, each listed; the generated property over placements is `TASK-393`.

## Acceptance Criteria

- [ ] From the main checkout on `main`, `ticket_ids()` includes a ticket only in the working tree (uncommitted), one only on `main`, one only on `task-<n>` (its own ticket), one only on `origin/task-<n>`, one retitled on `task-<n>` (file renamed there, `main` keeping the old name; listed once), and one deleted on its branch but present on `main`; it excludes a ticket only on branch `feature` and a file for `TASK-9` committed only on `task-5`
- [ ] A file named `notes.md` committed in `chitty/tasks/` on `main` makes `ticket_ids()` raise `main:chitty/tasks/notes.md: <problem>`; the same file in the working tree raises `<absolute path>: <problem>`; the same file committed only on `task-5` is ignored; with the configured main branch having no commit, `ticket_ids()` lists the working tree and ticket branch tickets without failing
- [ ] Outside a Git repository, `ticket_ids()` lists the working-tree tickets and, with every `chitty.git` function wrapped to record calls from after `Repo.open` returns, calls none except `git.is_repository`. In a repository with `main` and ticket branches `task-1` and `task-2`, with every `chitty.git` function wrapped, `ticket_ids()` calls `git.files_at` exactly once each for `refs/heads/main`, `refs/heads/task-1` and `refs/heads/task-2`, and never calls `git.historical_files` or `git.file_at`. `make check` passes with no existing test changed (`git diff main --stat -- tests` lists only the new file)

## Plan

Add a cached ID and ref-file index using filesystem scans and one Git tree read per eligible ref; validate main and working-tree entries while filtering ticket branches to their own ID. Add real-Git tests first against a NotImplementedError stub, then implement and run formatting and checks.

## Notes

Planner, 2026-11-20: split after the worker found it too large for one session. This ticket now only lists ticket IDs; choosing and reading copies moved to `TASK-476`, with tests in `TASK-477` and `TASK-478`.

All seven new real-Git tests were run against the NotImplementedError stub; each failed at ticket_ids as intended. Merged main into the ticket branch to resolve the earlier stale-ticket edit refusal.

Criterion 3 requires wrapping every chitty.git function and observing only git.is_repository outside Git, but git.is_repository itself calls git.repository_answer. The requested test therefore fails even when ticket_ids directly calls no other Git function. Decide whether to count only direct calls from ticket_ids, or change the existing Git helper despite the scope limiting this ticket to new Repo methods. Partial implementation and tests are committed; all seven tests failed against the required stub, and make check now fails only on this call-count assertion. Further verification and review remain unfinished.

Planner, 2026-11-20: the call-count question is settled in the Description: only outermost `chitty.git` calls are recorded, so the helper `git.is_repository` calls itself does not count. Keep the committed work and continue.

## History

- 2026-11-20T12:35:43Z jolly-dusky-badger → planning
- 2026-11-20T12:35:53Z jolly-dusky-badger planning → cold-read
- 2026-11-20T12:37:38Z jolly-dusky-badger: changed description, acceptance criteria
- 2026-11-20T12:37:38Z jolly-dusky-badger cold-read → planning
- 2026-11-20T12:37:42Z jolly-dusky-badger planning → cold-read
- 2026-11-20T12:39:12Z jolly-dusky-badger: changed description, acceptance criteria
- 2026-11-20T12:39:12Z jolly-dusky-badger cold-read → planning
- 2026-11-20T12:39:15Z jolly-dusky-badger planning → cold-read
- 2026-11-20T12:41:08Z jolly-dusky-badger: changed description, acceptance criteria
- 2026-11-20T12:41:08Z jolly-dusky-badger cold-read → planning
- 2026-11-20T12:42:03Z jolly-dusky-badger planning → cold-read
- 2026-11-20T12:43:40Z jolly-dusky-badger: changed description, acceptance criteria
- 2026-11-20T12:43:40Z jolly-dusky-badger cold-read → todo
- 2026-11-20T13:07:50Z eager-maroon-stoat todo → doing
- 2026-11-20T13:08:45Z eager-maroon-stoat: changed notes
- 2026-11-20T13:08:45Z eager-maroon-stoat doing → error
- 2026-11-20T17:23:10Z jolly-dusky-badger: replaced notes
- 2026-11-20T17:23:10Z jolly-dusky-badger error → todo
- 2026-11-20T17:25:12Z honest-quartz-jay todo → doing
- 2026-11-20T17:26:54Z human: changed owner, notes
- 2026-11-20T17:26:54Z human doing → planning
- 2026-11-20T17:31:16Z jolly-dusky-badger: replaced notes; changed description, acceptance criteria
- 2026-11-20T17:31:16Z jolly-dusky-badger planning → cold-read
- 2026-11-20T17:32:47Z jolly-dusky-badger: changed description, acceptance criteria
- 2026-11-20T17:32:47Z jolly-dusky-badger cold-read → todo
- 2026-11-20T17:35:15Z vivid-amber-lapwing todo → doing
- 2026-11-20T17:38:34Z vivid-amber-lapwing: changed owner, notes
- 2026-11-20T17:38:34Z vivid-amber-lapwing doing → planning
- 2026-11-20T17:43:58Z jolly-dusky-badger: replaced notes; changed title, owner, description, acceptance criteria
- 2026-11-20T17:43:58Z jolly-dusky-badger planning → cold-read
- 2026-11-20T17:45:19Z jolly-dusky-badger: changed description
- 2026-11-20T17:45:19Z jolly-dusky-badger cold-read → todo
- 2026-11-20T18:59:34Z open-ochre-badger todo → doing
- 2026-11-20T19:02:17Z open-ochre-badger: wrote the plan
- 2026-11-20T19:03:04Z open-ochre-badger: changed notes
- 2026-11-20T19:04:45Z open-ochre-badger: changed owner, notes
- 2026-11-20T19:04:45Z open-ochre-badger doing → planning
- 2026-11-20T19:05:52Z jolly-dusky-badger: changed description, notes
- 2026-11-20T19:05:52Z jolly-dusky-badger planning → todo
- 2026-11-20T19:08:35Z friendly-zinc-urchin todo → doing
- 2026-11-20T19:09:27Z friendly-zinc-urchin: changed notes
- 2026-11-20T19:09:27Z friendly-zinc-urchin doing → error
- 2026-11-20T19:10:36Z jolly-dusky-badger: replaced notes
- 2026-11-20T19:10:36Z jolly-dusky-badger error → doing
