---
title: Read single tickets from their authoritative source, not every ref's history
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
  - TASK-479
  - TASK-482
  - TASK-504
  - TASK-505
parent: TASK-376
created: 2026-11-18
---

## Description

On `main` today, `Repo.lookup` and `Repo.context_of` in `src/chitty/store.py` find a ticket through `_tasks_in_location`, which reads every ref's history (`self._history()`, from `git.historical_files`) and takes the copy with the newest commit time, which picks wrong copies (`TASK-366`). `Repo.source_copy(task_id)` (`TASK-476`, tested further by `TASK-477` and `TASK-478`) applies the decided rule (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands: `git show plan/ticket-state:docs/plan/ticket-state.md`) but no read uses it. This ticket switches single-ticket reads (`lookup`, `find`, `context_of`, so `chitty show`, `edit`, `note` and the runner's per-ticket reads) to it and migrates the tests that assert the old choice. Split again on 2026-11-21 when a worker found it too large: the own-worktree write rule is `TASK-482` (lands first) and reference checks by ID are `TASK-483` (lands after).

Split on 2026-11-20 after three cold reads found serious gaps in the whole switch: context discovery is `TASK-479` (done; already a dependency), and listing (`_tasks_in_location`, `chitty list`, and multi-ticket writes) is `TASK-480`, which starts after this ticket.

The earlier attempt (commits `27456731` to `bed36801`, reverted by `0ac2ee94`) is kept as tag `task-378-attempt`; `TASK-474` and `TASK-476` supersede it. Branch `task-378` was rebuilt on 2026-11-20 as `main` plus this ticket's text.

Measured 2026-11-21 with a spike, commit `ab2ac7bf` on branch `spike/task-378` (about 40 lines in `src/chitty/store.py`; not reviewed). The worker may start from it (`git cherry-pick ab2ac7bf`, then add the `Task: TASK-378` trailer) or write the same change. With it, after `TASK-504` and `TASK-505` land, exactly the 9 tests named in the migration decision fail and nothing else does (measured 2026-11-21 in scratch worktrees); `tests/test_list_performance.py` passes.

Decisions:

- `lookup(task_id)` returns `None` when `source_copy(task_id)` is `None`, and otherwise a `StoredTask` built from the copy: context from `path.parts[1]` (the `Context` of that name from `discovered_contexts()`), archived exactly when `path.parts[2] == "archive"`. It no longer calls `_tasks_in_location`. `context_of(task_id)` returns the context of the source copy, falling back, only when there is no copy, to the configured context whose prefix matches, and otherwise raising today's `no context in <root> has prefix` `ChittyError` (as `7b12d835` does); it never lists tasks and never parses: split the source choice and file listing out of `source_copy` into a private `_source_files(task_id) -> tuple[str, list[tuple[Path, str]]]` (the ref and its unparsed files), which `source_copy` then parses and `context_of` reads only the first path of. Without this, `tests/test_next.py` `test_dependency_check_parses_only_the_dependency` counts two parses instead of one; it must pass unchanged. `find` is unchanged apart from using them.
- `TASK-504` (lands first) makes `_choose_source` parse nothing, so the `_source_files` split above is enough for `context_of` never to parse.
- `StoredTask.branch` is `SourceCopy.ref` (`task-5`, `origin/task-5`, `main`, or `None` for the working tree); `show` keeps printing `branch:` (`src/chitty/cli.py`), now with the source copy's ref. `StoredTask.path` is this checkout's root joined with the copy's relative path, whether or not that file exists here.
- Rule decided with the owner 2026-11-20: an operation fails only if it needs the conflicted ticket's content. Here that means errors from `source_copy` propagate only from reads of that ticket: `chitty show`, `edit` and `note` keep working for other tickets while one is conflicted. Reference checks (`check.check`, `check_dependencies`, the `parent` checks) still go through `lookup` here, so a ticket that references a conflicted ticket cannot be edited until `TASK-483` (which starts after this) checks references by ID.
- The write allowance for a ticket's own fresh worktree is `TASK-482`, which lands first: without it, the first write in a fresh ticket worktree (including the runner's claim) would be refused once the ticket is read from `main`.
- Visible behaviour changes (label `needs-minor`): on a branch that is neither `main` nor the ticket's own branch, `show` reads an existing ticket from `main`'s tip (an uncommitted edit there is not shown) and `_require_current_version` refuses to write it; a ticket branch merged into `main` no longer hides `main`'s copy; with the configured main branch absent, reading a ticket that has no ticket branch from a checkout not on that branch fails with `configured main branch ... has no tip`; `show` of a ticket only on an unrelated branch fails with `no task`.
- Unchanged here and left to `TASK-480`: the multi-ticket writes (`new_id` on a ticket branch, `archive_done`, `_delete_done`, `move`, `renumber`), which still act on the copies `all_tasks()` picks from history, and `_set_archived`, which renames `StoredTask.path` as today. Also unchanged: `_tasks_in_location`, `tasks`, `all_tasks` and `chitty list` (`TASK-480`), `next_number` (`TASK-379`), `check.py`, and `_dependency_is_done`, which keeps reading dependencies from `main`'s files. `_history()` stays, still used by `_tasks_in_location`.
- Migrations: exactly these 9 tests change, without deleting or weakening any other assertion. The exact code is commit `73f2cf97` on branch `spike/task-378-migrations` (planner spike, not reviewed), on top of `7b12d835`, which is spike `ab2ac7bf` rebased onto `main` after `TASK-504` and `TASK-505`. Measured 2026-11-21 with both commits: the full suite passes apart from five formatter and `init` guide tests that fail in a scratch environment without prettier, with or without the change. Start with `git cherry-pick 7b12d835 73f2cf97` and add the `Task: TASK-378` trailer to both. The changes:
  - `tests/test_check_cross_branch_references.py` `test_reference_existence_matches_show`: the "other branch" row becomes `("other branch", True)`, and `show` is expected to exit 1 for it: `exit_code=1 if location in {"nowhere", "other branch"} else 0`.
  - Same file, `test_malformed_task_on_another_branch_reports_parse_error` becomes `test_malformed_task_on_another_branch_is_not_read`: `check` now reports `depends_on TASK-3: no such task` in `result.stdout`, and `file must start with '---' frontmatter` is not in `result.stderr`.
  - Same file, `test_edit_can_depend_on_task_only_on_main` becomes `test_edit_on_another_branch_is_refused`: `edit 1 --depends-on 2` on branch `b` exits 1 with `latest committed version is on branch main` in `stderr`; the working tree stays clean, and `TASK-2` is not added to `TASK-1`'s file.
  - `tests/test_next.py` `test_todo_dependency_must_be_done_on_main` and `test_unmerged_archive_does_not_complete_dependency`: each string literal `"worker"` or `"rename"` that appears becomes `"task-1"`, the dependency's own branch; nothing else changes.
  - `tests/test_next.py` `test_run_from_another_worktree_uses_the_branch_not_main`: the newer note is committed on `task-1` (`checkout -b task-1`, `edit TASK-1 --note "newer copy on task-1"`, `checkout main`) instead of on `main`, which would now be the changed-on-both error; the runner assertions stay.
  - `tests/test_store.py` `test_numbers_ignore_committed_tasks_on_another_branch`: the branch's two tickets are written as files (`archive/TASK-1--archived-branch-task.md`, `TASK-2--active-branch-task.md`) and committed with Git, not made through `Repo`; the numbering assertions stay.
  - `tests/test_repair_requires_work.py`, the `uncommitted` case gets its own branch of the `if`: it expects `repair agent left TASK-1 in invalid status error; expected review or blocked` in `stderr`, and the main checkout's ticket file still says `status: error`. The `edit` case keeps its assertions.
  - `tests/test_provisional_ids.py` `test_move_provisional_off_main_then_promote_on_main`: on `feature`, `move TASK-1 human` exits 1 with `latest committed version is on branch main`; then, with `_provisional_draw` patched to 0, `add Branch` gives `TASK-AAAAAA` and `move TASK-AAAAAA human` gives `HUMAN-AAAAAA`. Promotion now gives `TASK-2`, because `main` still holds `TASK-1`.
  - Unchanged and passing: `test_ticket_worktree_write_does_not_wait` (`tests/test_main_checkout_lock.py`), `tests/test_list_performance.py` and `test_dependency_check_parses_only_the_dependency`.
  If `make check` shows any other failure, it is not a planned migration: return the ticket to `planning` naming it.
- One ticket: these migrations cannot land apart from the switch without `make check` failing in between. The renames that pass before and after are `TASK-505`; the ID rule is `TASK-504`; the CLI wiring tests are `TASK-506`, which starts after this lands. `TASK-474` to `TASK-478` already test each placement directly.

Tests: no new test file here (`TASK-506` adds them). The migrated tests assert the new behaviour. `make check` takes about a minute; run it with a shell timeout of at least five minutes. No property: the generated property over placements is `TASK-393`.

## Acceptance Criteria

- [ ] The two spike commits are applied (or the same change written), and the 9 migrated tests are as the Decisions describe. The five that assert new behaviour (the three in `tests/test_check_cross_branch_references.py`, the repair `uncommitted` case and the provisional migration) each fail on `main` before the switch, recorded in a note. To get that evidence, commit your work first, then run `git show main:src/chitty/store.py > src/chitty/store.py`, run those tests, and restore with `git checkout -- src/chitty/store.py`.
- [ ] `make check` passes, with every test in `tests/test_list_performance.py`, `test_dependency_check_parses_only_the_dependency` and `test_ticket_worktree_write_does_not_wait` passing unchanged; the review note lists every existing test the branch changed, each with its old and new assertion

## Plan

Add real-Git regression coverage and confirm failures before the switch; route single-ticket reads through unparsed source selection, migrate the specified tests, then format, check and hand off.

## Notes

Earlier notes (attempts, splits, cold reads, workers' returns) are in Git history; the Description is authoritative.

Split 2026-11-21: the ID rule (`TASK-504`) and six renames (`TASK-505`) have landed; the CLI read tests are `TASK-506`, after this. A worker then found the provisional and two `test_next.py` migrations underspecified; the planner measured exact replacements on `main` plus spike `ab2ac7bf` and wrote them into the Description.

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
- 2026-11-20T22:20:23Z calm-fawn-raven: wrote the plan
- 2026-11-20T22:21:18Z calm-fawn-raven: changed owner, notes
- 2026-11-20T22:21:18Z calm-fawn-raven doing → planning
- 2026-11-20T22:38:13Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T22:38:32Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T22:38:32Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T22:40:23Z quick-pearl-lapwing: changed notes
- 2026-11-20T22:40:23Z quick-pearl-lapwing cold-read → planning
- 2026-11-20T22:55:43Z quick-pearl-lapwing: changed notes
- 2026-11-20T22:58:04Z quick-pearl-lapwing: changed dependencies, description
- 2026-11-20T22:59:44Z quick-pearl-lapwing: changed title, dependencies, description, acceptance criteria, notes
- 2026-11-20T22:59:44Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T23:01:44Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T23:02:43Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T23:02:43Z quick-pearl-lapwing cold-read → todo
- 2026-11-21T01:12:21Z rosy-russet-adder todo → doing
- 2026-11-21T01:18:00Z rosy-russet-adder: changed notes
- 2026-11-21T01:18:34Z rosy-russet-adder: changed owner, notes
- 2026-11-21T01:18:34Z rosy-russet-adder doing → planning
- 2026-11-21T01:22:55Z quick-pearl-lapwing: changed dependencies, description, acceptance criteria, notes
- 2026-11-21T01:23:50Z quick-pearl-lapwing planning → cold-read
- 2026-11-21T01:25:15Z quick-pearl-lapwing: changed description, acceptance criteria, notes
- 2026-11-21T01:25:15Z quick-pearl-lapwing cold-read → todo
- 2026-11-21T01:50:03Z eager-violet-puffin todo → doing
- 2026-11-21T01:54:02Z eager-violet-puffin: wrote the plan
- 2026-11-21T01:54:48Z eager-violet-puffin: changed notes
- 2026-11-21T01:55:12Z eager-violet-puffin: changed owner, notes
- 2026-11-21T01:55:12Z eager-violet-puffin doing → planning
- 2026-11-21T09:07:56Z nimble-umber-gannet: changed description, acceptance criteria, notes; wrote the plan
- 2026-11-21T09:07:56Z nimble-umber-gannet planning → cold-read
- 2026-11-21T09:08:18Z nimble-umber-gannet: changed acceptance criteria
- 2026-11-21T09:10:42Z nimble-umber-gannet: replaced notes; changed description, acceptance criteria
- 2026-11-21T09:10:42Z nimble-umber-gannet cold-read → todo
- 2026-11-21T09:11:04Z nimble-umber-gannet todo → cold-read
- 2026-11-21T09:12:19Z nimble-umber-gannet: changed description, acceptance criteria, notes
- 2026-11-21T09:12:19Z nimble-umber-gannet cold-read → todo
- 2026-11-21T10:45:47Z witty-ochre-vole todo → doing
- 2026-11-21T10:49:29Z witty-ochre-vole: changed owner, notes
- 2026-11-21T10:49:29Z witty-ochre-vole doing → planning
- 2026-11-21T11:25:55Z sunny-ebony-kestrel: changed description, acceptance criteria, notes
- 2026-11-21T11:25:55Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T11:29:13Z sunny-ebony-kestrel: replaced notes; changed description, acceptance criteria
- 2026-11-21T11:29:13Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T11:29:45Z golden-khaki-vole todo → doing
- 2026-11-21T11:31:46Z golden-khaki-vole: wrote the plan
- 2026-11-21T11:32:08Z golden-khaki-vole: changed owner, notes
- 2026-11-21T11:32:08Z golden-khaki-vole doing → planning
- 2026-11-21T11:34:58Z sunny-ebony-kestrel: changed dependencies
- 2026-11-21T11:41:04Z sunny-ebony-kestrel: replaced notes; changed dependencies, description, acceptance criteria
- 2026-11-21T11:41:04Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T11:42:40Z sunny-ebony-kestrel: changed acceptance criteria
- 2026-11-21T11:42:40Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T12:01:59Z daring-russet-raven todo → doing
- 2026-11-21T12:04:13Z daring-russet-raven: changed owner, notes
- 2026-11-21T12:04:13Z daring-russet-raven doing → planning
- 2026-11-21T12:06:08Z sunny-ebony-kestrel: replaced notes; changed description, acceptance criteria
- 2026-11-21T12:06:08Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T12:12:41Z sunny-ebony-kestrel: changed description, acceptance criteria
- 2026-11-21T12:14:09Z sunny-ebony-kestrel: changed description, acceptance criteria
- 2026-11-21T12:14:09Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T12:14:54Z quick-amber-jay todo → doing
