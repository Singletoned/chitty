---
title: Read each ticket from its authoritative ref, not every ref's history
status: doing
labels:
  - needs-minor
depends_on:
  - TASK-377
  - TASK-382
  - TASK-383
  - TASK-396
  - TASK-380
  - TASK-474
  - TASK-475
  - TASK-384
  - TASK-476
  - TASK-477
  - TASK-478
parent: TASK-376
created: 2026-11-18
---

## Description

On `main` today, `Repo._tasks_in_location` and `Repo.discovered_contexts` in `src/chitty/store.py` read every ref's history (`self._history()`, from `git.historical_files`) and take each ticket's copy with the newest commit time, which picks wrong copies (`TASK-366`). `TASK-474` adds `Repo.ticket_ids()` and `TASK-476` adds `Repo.source_copy(task_id)` (tested further by `TASK-477` and `TASK-478`), which apply the decided rule (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands: `git show plan/ticket-state:docs/plan/ticket-state.md`) but are not used by any read. This ticket switches every ticket read to them, adds the write rule a fresh ticket worktree needs, and migrates the tests that assert the old choice.

Starts after `TASK-474`, `TASK-476`, `TASK-477`, `TASK-478`, `TASK-475` and `TASK-384` land. `TASK-384` makes the runner claim a ticket on its branch instead of on `main`; with the runner still claiming on `main`, the new reads see a ticket with a branch as changed on both sides, which blocked this ticket on 2026-11-20.

The runner may take it: it was held for a person after runner claims on `main` conflicted with the new reads, which `TASK-384` has since fixed.

The earlier attempt (commits `27456731` to `bed36801`, reverted by `0ac2ee94`) is kept as tag `task-378-attempt`; `TASK-474` and `TASK-476` supersede it. Branch `task-378` was rebuilt on 2026-11-20 as `main` plus this ticket's text, so its code is `main`'s.

Decisions:

- Wiring: `_tasks_in_location` lists, for its context and archived flag, the IDs from `ticket_ids()` whose `source_copy` is in that directory, as `StoredTask`s built from the copy; `lookup` reads `source_copy` for its ID; `discovered_contexts` takes configured contexts plus every context directory holding a source copy or a working-tree ticket; `context_of` takes the context of the source copy, falling back to the prefix only when there is none. An ID is listed once, in whichever directory holds its source copy, and is archived exactly when that copy's path is under the context's `archive` directory. `_history()` has no other callers than these two methods, so after the switch nothing calls `git.historical_files` (criterion 4 relies on this); outside a Git repository `ticket_ids()` and `source_copy` already read only the working tree.
- `StoredTask.branch` is `SourceCopy.ref` (`task-5`, `origin/task-5`, `main`, or `None` for the working tree); `show` keeps printing `branch:` (`src/chitty/cli.py`), now with the source copy's ref. `StoredTask.path` is this checkout's root joined with the copy's relative path, whether or not that file exists here.
- Errors from `source_copy` propagate only from reads of that ticket: `chitty show`, `edit` and the runner keep working for other tickets while one is conflicted; `chitty list` reads every ticket and fails naming the conflicted ticket; this ticket does not make it list the others.
- Writes in the ticket's own worktree (owner, 2026-11-20): `_require_current_version` also allows a write when the current branch is the ticket's own branch (`task-5` for `TASK-5`), the ticket's source is `main`, and `git.changed_since_split(root, "refs/heads/<configured main branch>", "refs/heads/task-5", paths)` is false, with `paths` the union of the relative paths returned by `self._ref_ticket_files(ref, <ID>)` for those two refs (the files `source_copy` reads; call `ticket_ids()` first so the cache is filled). The write commits on the branch, which puts it ahead of `main`, so every checkout then reads the ticket from there. A merged branch that `main` has since changed is still refused. Every other case is refused as today; `TASK-385` replaces the guard later.
- Visible behaviour changes (label `needs-minor`): on a branch that is neither `main` nor the ticket's own branch, an existing ticket is read from `main`'s tip (an uncommitted edit there is not shown) and `_require_current_version` refuses to write it; a ticket branch merged into `main` no longer hides `main`'s copy; with the configured main branch absent, reading a ticket that has no ticket branch from a checkout not on that branch fails with `configured main branch ... has no tip`; a ticket only on an unrelated branch is no longer listed.
- Unchanged: `next_number` (`TASK-379`), `check.py`'s `check` and `fix`, and `_dependency_is_done`, which keeps reading dependencies from `main`'s files. `TASK-386` deletes the history code; this ticket only stops calling it.
- Migrate, without deleting or weakening any: in `tests/test_check_cross_branch_references.py`, the "other branch" row of `test_reference_existence_matches_show` (`missing` becomes `True`), `test_malformed_task_on_another_branch_reports_parse_error` (now `no task`) and `test_edit_can_depend_on_task_only_on_main` (now refused on a non-ticket branch); `tests/test_unconfigured_directories.py` `test_finds_directory_that_exists_only_in_branch_history` (now not found); in `tests/test_next.py`, `test_todo_dependency_must_be_done_on_main` and `test_unmerged_archive_does_not_complete_dependency` (writes from branches `worker` and `rename` now refused; reads from `main`); in `tests/test_cli.py`, rename branch `worker` to `task-1` in `test_allows_writes_in_the_branch_with_the_latest_version` and `test_allows_writes_from_a_new_worktree_with_no_commits_of_its_own`, keeping their assertions, and keep `test_refuses_all_single_ticket_writes_from_another_worktree`, `test_refuses_a_branch_without_a_worktree` and `test_refuses_a_remote_tracking_branch` asserting exit 1 with the `_require_current_version` message (`latest committed version is on branch <ref>`, naming the ref the ticket is now read from), and no commit made; `test_ticket_worktree_write_does_not_wait` in `tests/test_main_checkout_lock.py` must pass through the own-worktree rule. Migrate any other test `make check` shows asserting the old choice the same way, and name it in the review note. Keep `tests/test_list_performance.py` passing.
- One ticket: the migrations cannot land apart from the switch without `make check` failing in between. `TASK-474` to `TASK-478` already test each placement directly, so this ticket's new tests check the CLI wiring only.

Tests: real-Git CLI tests in a new `tests/test_ticket_reads.py`, inheriting `CliTestCase` from `tests/test_cli.py`, set up as `tests/test_check_cross_branch_references.py` does. No property: a fixed set of cases, each in the criteria; the generated property over placements is `TASK-393`.

## Acceptance Criteria

- [ ] From the main checkout, through the CLI: a ticket edited on `task-<n>` ahead of `main` shows the branch copy in `chitty show`, which prints `branch: task-<n>`; a ticket retitled on `task-<n>` is listed once by `chitty list` with the branch title, and `chitty show` prints the branch path; a ticket archived on its branch is listed once, as archived, by `chitty list --all`; a ticket only on branch `feature` is not listed and `chitty show` fails with `no task` (fails before the change)
- [ ] In the linked worktree of a fresh `task-6` made at `main`'s tip, `chitty edit TASK-6 --note x` succeeds and commits on `task-6`, after which `chitty show TASK-6` in the main checkout prints `branch: task-6`; after `task-6` is fast-forward merged into `main` and a further `main` commit changes `TASK-6`, the same edit in that worktree exits 1 with the `_require_current_version` message naming `main`
- [ ] With `TASK-1` edited on both `task-1` and `main` since they split, and `TASK-2` only on `main`: `chitty show TASK-2` and `chitty edit TASK-2 --note x` succeed; `chitty show TASK-1` fails naming `task-1` and `main`; `chitty list` fails naming `TASK-1`. With a file not starting with `---` committed as `TASK-1` on `task-1`, `chitty show TASK-1` fails with `task-1:<its relative path>: file must start with '---' frontmatter`. In a linked worktree on branch `feature`, an uncommitted retitle of `TASK-2` there is not shown: `chitty show TASK-2` prints the title committed on `main`
- [ ] With `git.historical_files` patched (`unittest.mock.patch.object`) to raise, `chitty list` and `chitty show` give criterion 1's results (fails before the change); outside a Git repository, `chitty list` reads the working tree (a regression guard that passes before the change; the review note says so)
- [ ] Every test named in the migration decision, and every other test that fails after the switch because it asserted the old choice, asserts its new behaviour without being deleted or weakened, and the review note lists each by name with its result; `tests/test_list_performance.py` passes; `make check` passes

## Notes

Planner, 2026-11-20: ticket rewritten as the read switch only. The lookup it builds on is `TASK-474`, `TASK-476`, `TASK-477`, `TASK-478` and `TASK-475`, and the runner claim change is `TASK-384`, all landing first. Earlier notes, including about 90 KB of pasted check output, are in Git history. Stays in `planning` until those are done; then compare this text with what landed, cold-read it, and move it to `todo`. Owner `human` keeps `chitty run` off it; start its worker by hand.

Owner `human` cleared 2026-11-20 at the owner's request: `TASK-384` removed the reason it was held back from `chitty run`. Earlier notes saying to start its worker by hand no longer apply. If a runner session cannot finish it, return it to `planning` to be split further.

## History

- 2026-11-18T16:20:04Z lively-quartz-crane → backlog
- 2026-11-18T16:20:27Z lively-quartz-crane: changed title
- 2026-11-18T16:23:16Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:32:51Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:32:51Z lively-quartz-crane backlog → planning
- 2026-11-18T16:33:20Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:38:58Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:38:58Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:39:00Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T16:40:28Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:52:27Z lively-quartz-crane: changed labels, dependencies, description, acceptance criteria
- 2026-11-18T17:52:27Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:52:44Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:55:29Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:55:29Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:55:31Z lively-quartz-crane planning → todo
- 2026-11-18T17:58:22Z lively-quartz-crane: changed description
- 2026-11-19T14:43:37Z tidy-yellow-lapwing todo → doing
- 2026-11-19T14:54:48Z tidy-yellow-lapwing: wrote the plan
- 2026-11-19T15:21:14Z tidy-yellow-lapwing: changed owner, notes, summary
- 2026-11-19T15:21:14Z tidy-yellow-lapwing doing → planning
- 2026-11-20T09:26:02Z lively-bronze-crane: changed description
- 2026-11-20T09:26:19Z lively-bronze-crane: changed acceptance criteria
- 2026-11-20T09:26:23Z lively-bronze-crane planning → cold-read
- 2026-11-20T09:28:17Z lively-bronze-crane: changed dependencies
- 2026-11-20T09:28:17Z lively-bronze-crane cold-read → planning
- 2026-11-20T09:28:20Z lively-bronze-crane: changed description
- 2026-11-20T09:28:34Z lively-bronze-crane: changed description, acceptance criteria
- 2026-11-20T09:28:38Z lively-bronze-crane planning → cold-read
- 2026-11-20T09:28:49Z lively-bronze-crane cold-read → planning
- 2026-11-20T09:28:52Z lively-bronze-crane: changed acceptance criteria
- 2026-11-20T09:28:54Z lively-bronze-crane planning → cold-read
- 2026-11-20T09:30:43Z lively-bronze-crane cold-read → planning
- 2026-11-20T09:30:45Z lively-bronze-crane: changed description, acceptance criteria, notes
- 2026-11-20T09:30:50Z lively-bronze-crane planning → todo
- 2026-11-20T09:31:03Z plucky-bronze-gannet todo → doing
- 2026-11-20T09:44:51Z human: changed notes
- 2026-11-20T09:44:51Z human doing → blocked
- 2026-11-20T10:05:47Z lively-bronze-crane: changed owner, notes
- 2026-11-20T10:05:47Z lively-bronze-crane blocked → doing
- 2026-11-20T10:16:03Z plucky-white-dormouse: changed owner, notes, summary
- 2026-11-20T10:16:03Z plucky-white-dormouse doing → planning
- 2026-11-20T11:09:47Z lively-bronze-crane: changed description, acceptance criteria, notes
- 2026-11-20T11:10:00Z lively-bronze-crane: changed acceptance criteria
- 2026-11-20T11:15:04Z lively-bronze-crane: changed description, acceptance criteria
- 2026-11-20T11:15:27Z lively-bronze-crane planning → cold-read
- 2026-11-20T11:17:33Z lively-bronze-crane cold-read → planning
- 2026-11-20T11:17:35Z lively-bronze-crane: changed description, acceptance criteria
- 2026-11-20T11:17:40Z lively-bronze-crane planning → cold-read
- 2026-11-20T11:19:27Z lively-bronze-crane cold-read → planning
- 2026-11-20T11:19:29Z lively-bronze-crane: changed description, acceptance criteria
- 2026-11-20T11:19:34Z lively-bronze-crane planning → cold-read
- 2026-11-20T11:20:47Z lively-bronze-crane cold-read → planning
- 2026-11-20T11:20:50Z lively-bronze-crane: changed description, acceptance criteria, notes
- 2026-11-20T11:20:56Z lively-bronze-crane: changed owner
- 2026-11-20T11:20:56Z lively-bronze-crane planning → doing
- 2026-11-20T11:59:01Z lively-pearl-zander: changed notes
- 2026-11-20T12:00:02Z lively-pearl-zander: changed owner, notes
- 2026-11-20T12:00:02Z lively-pearl-zander doing → planning
- 2026-11-20T12:01:52Z lively-bronze-crane: replaced notes
- 2026-11-20T12:01:55Z lively-bronze-crane: changed owner
- 2026-11-20T12:01:55Z lively-bronze-crane planning → doing
- 2026-11-20T12:03:20Z nimble-violet-gannet: changed notes
- 2026-11-20T12:13:58Z nimble-violet-gannet: changed owner, notes
- 2026-11-20T12:13:58Z nimble-violet-gannet doing → planning
- 2026-11-20T12:45:22Z jolly-dusky-badger: replaced notes; changed owner, dependencies, description, acceptance criteria, summary; wrote the plan
- 2026-11-20T17:44:55Z jolly-dusky-badger: replaced notes; changed dependencies, description
- 2026-11-20T17:45:05Z jolly-dusky-badger: changed description
- 2026-11-20T22:07:36Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T22:08:36Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T22:09:37Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T22:09:37Z quick-pearl-lapwing cold-read → todo
- 2026-11-20T22:18:48Z quick-pearl-lapwing: changed owner, description, notes
- 2026-11-20T22:18:52Z calm-fawn-raven todo → doing
