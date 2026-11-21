---
title: Read single tickets from their authoritative source, not every ref's history
status: cold-read
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
parent: TASK-376
created: 2026-11-18
---

## Description

On `main` today, `Repo.lookup` and `Repo.context_of` in `src/chitty/store.py` find a ticket through `_tasks_in_location`, which reads every ref's history (`self._history()`, from `git.historical_files`) and takes the copy with the newest commit time, which picks wrong copies (`TASK-366`). `Repo.source_copy(task_id)` (`TASK-476`, tested further by `TASK-477` and `TASK-478`) applies the decided rule (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands: `git show plan/ticket-state:docs/plan/ticket-state.md`) but no read uses it. This ticket switches single-ticket reads (`lookup`, `find`, `context_of`, so `chitty show`, `edit`, `note` and the runner's per-ticket reads) to it and migrates the tests that assert the old choice. Split again on 2026-11-21 when a worker found it too large: the own-worktree write rule is `TASK-482` (lands first) and reference checks by ID are `TASK-483` (lands after).

Split on 2026-11-20 after three cold reads found serious gaps in the whole switch: context discovery is `TASK-479` (starts after it lands), and listing (`_tasks_in_location`, `chitty list`, and multi-ticket writes) is `TASK-480`, which starts after this ticket.

The earlier attempt (commits `27456731` to `bed36801`, reverted by `0ac2ee94`) is kept as tag `task-378-attempt`; `TASK-474` and `TASK-476` supersede it. Branch `task-378` was rebuilt on 2026-11-20 as `main` plus this ticket's text.

Measured 2026-11-21 with a spike, commit `ab2ac7bf` on branch `spike/task-378` (about 40 lines in `src/chitty/store.py`; not reviewed). The worker may start from it (`git cherry-pick ab2ac7bf`, then add the `Task: TASK-378` trailer) or write the same change. With it, exactly the 15 tests named in the migration decision fail and nothing else does; `tests/test_list_performance.py` passes. The switch is small; the migrations are most of the work, and each is spelled out below.

Decisions:

- `lookup(task_id)` returns `None` when `source_copy(task_id)` is `None`, and otherwise a `StoredTask` built from the copy: context from `path.parts[1]` (the `Context` of that name from `discovered_contexts()`), archived exactly when `path.parts[2] == "archive"`. It no longer calls `_tasks_in_location`. `context_of(task_id)` returns the context of the source copy, falling back to the prefix as today only when there is none; it never lists tasks and never parses: split the source choice and file listing out of `source_copy` into a private `_source_files(task_id) -> tuple[str, list[tuple[Path, str]]]` (the ref and its unparsed files), which `source_copy` then parses and `context_of` reads only the first path of. Without this, `tests/test_next.py` `test_dependency_check_parses_only_the_dependency` counts two parses instead of one; it must pass unchanged. `find` is unchanged apart from using them.
- `StoredTask.branch` is `SourceCopy.ref` (`task-5`, `origin/task-5`, `main`, or `None` for the working tree); `show` keeps printing `branch:` (`src/chitty/cli.py`), now with the source copy's ref. `StoredTask.path` is this checkout's root joined with the copy's relative path, whether or not that file exists here.
- Rule decided with the owner 2026-11-20: an operation fails only if it needs the conflicted ticket's content. Here that means errors from `source_copy` propagate only from reads of that ticket: `chitty show`, `edit` and `note` keep working for other tickets while one is conflicted. Reference checks (`check.check`, `check_dependencies`, the `parent` checks) still go through `lookup` here, so a ticket that references a conflicted ticket cannot be edited until `TASK-483` (which starts after this) checks references by ID.
- The write allowance for a ticket's own fresh worktree is `TASK-482`, which lands first: without it, the first write in a fresh ticket worktree (including the runner's claim) would be refused once the ticket is read from `main`.
- Visible behaviour changes (label `needs-minor`): on a branch that is neither `main` nor the ticket's own branch, `show` reads an existing ticket from `main`'s tip (an uncommitted edit there is not shown) and `_require_current_version` refuses to write it; a ticket branch merged into `main` no longer hides `main`'s copy; with the configured main branch absent, reading a ticket that has no ticket branch from a checkout not on that branch fails with `configured main branch ... has no tip`; `show` of a ticket only on an unrelated branch fails with `no task`.
- Unchanged here and left to `TASK-480`: the multi-ticket writes (`new_id` on a ticket branch, `archive_done`, `_delete_done`, `move`, `renumber`), which still act on the copies `all_tasks()` picks from history, and `_set_archived`, which renames `StoredTask.path` as today. Also unchanged: `_tasks_in_location`, `tasks`, `all_tasks` and `chitty list` (`TASK-480`), `next_number` (`TASK-379`), `check.py`, and `_dependency_is_done`, which keeps reading dependencies from `main`'s files. `_history()` stays, still used by `_tasks_in_location`.
- Migrate exactly these 15 tests, without deleting or weakening any assertion (the spike shows they are the only ones the switch breaks):
  - `tests/test_check_cross_branch_references.py`: the "other branch" row of `test_reference_existence_matches_show` (`missing` becomes `True`); `test_malformed_task_on_another_branch_reports_parse_error` (now `no task`); `test_edit_can_depend_on_task_only_on_main` (now refused on a non-ticket branch).
  - `tests/test_cli.py`, all five tests in `TestCrossBranchWrites` that use branch `worker`: rename the branch, and its worktree directory, to `task-1`, so the ticket is read from it, and change every asserted `worker` to `task-1` (`git switch task-1`, `run Chitty in worktree <path>`). The two `test_allows_...` tests keep their assertions otherwise; the three `test_refuses_...` tests still assert exit 1, the `latest committed version is on branch task-1` message (or `origin/task-1` for the remote-tracking one) and no commit.
  - `tests/test_mcp.py` `test_cross_branch_write_error_matches_the_cli`: the same rename; it expects a `ToolError` matching `task-1`.
  - `tests/test_next.py` `test_todo_dependency_must_be_done_on_main` and `test_unmerged_archive_does_not_complete_dependency`: writes from branches `worker` and `rename` are now refused; reads come from `main`.
  - `tests/test_next.py` `test_run_from_another_worktree_uses_the_branch_not_main`: it edits `TASK-1` on `main` after `task-1` exists, which is now the changed-on-both error. Make the newer copy on `task-1` instead (commit the note on `task-1`, not `main`); the runner assertions stay.
  - `tests/test_store.py` `test_numbers_ignore_committed_tasks_on_another_branch`: on branch `other` it makes a non-provisional `TASK-1` and archives it through `Repo`, which is now refused. Write and `git mv` the branch's ticket files directly and commit them with Git; the numbering assertions stay.
  - `tests/test_repair_requires_work.py`, the `uncommitted` case: a fresh `task-1` level with `main` reads its ticket from `main`, so the agent's uncommitted `review` is not seen. It now expects `repair agent left TASK-1 in invalid status error; expected review or blocked`; the main checkout file still says `status: error`. The other cases stay.
  - `tests/test_provisional_ids.py` `test_move_provisional_off_main_then_promote_on_main`: moving `main`'s `TASK-1` on branch `feature` is now refused. Assert that refusal (`move TASK-1 human` exits 1 with `latest committed version is on branch main`), then make the provisional ticket with `add` in context `human` on `feature` instead, merge and promote it as today.
  - `test_ticket_worktree_write_does_not_wait` in `tests/test_main_checkout_lock.py` must still pass unchanged.
  If `make check` shows any other failure, it is not a planned migration: return the ticket to `planning` naming it.
- The `show` error texts in criterion 3 already exist: `_choose_source` raises the changed-on-both error and `_parse_source_copy` formats `<ref>:<path>: <error>`.
- One ticket: the migrations cannot land apart from the switch without `make check` failing in between. `TASK-474` to `TASK-478` already test each placement directly, so this ticket's new tests check the CLI wiring only.

Tests: real-Git CLI tests in a new `tests/test_ticket_reads.py`, inheriting `CliTestCase` from `tests/test_cli.py`, set up as `tests/test_check_cross_branch_references.py` does. Each criterion 1 fixture commits `main`'s tickets with `GIT_COMMITTER_DATE=2030-01-01T00:00:00Z` before the ticket branch is made, so today's newest-commit rule prefers `main`'s copy; without that date the branch-edit and retitle cases pass before the change. Checked 2026-11-21 against `main` and the spike: on `main` the branch edit shows `main`'s title, the retitle shows `main`'s path, the branch archive fails with `used by more than one file`, the `feature`-only ticket is shown, and the malformed branch copy shows `main`'s copy; with the spike each gives the criterion's result. No property: a fixed set of cases, each in the criteria; the generated property over placements is `TASK-393`.

## Acceptance Criteria

- [ ] From the main checkout, through the CLI: `chitty show` of a ticket edited on `task-<n>` ahead of `main`, with an unrelated commit on `main` made after the branch edit (so today's newest-commit rule picks `main`'s copy), prints the branch copy and `branch: task-<n>`; of a ticket retitled on `task-<n>`, prints the branch path; of a ticket archived on its branch, prints its archive path; of a ticket only on branch `feature`, fails with `no task` (each fails before the change)
- [ ] With `TASK-1` edited on both `task-1` and `main` since they split, and `TASK-2` only on `main`: `chitty show TASK-2` succeeds; `chitty show TASK-1` fails naming `task-1` and `main` (fails before the change). With a file not starting with `---` committed as `TASK-1` on `task-1`, `chitty show TASK-1` fails with `task-1:<its relative path>: file must start with '---' frontmatter`. In a linked worktree on branch `feature`, an uncommitted retitle of `TASK-2` there is not shown: `chitty show TASK-2` prints the title committed on `main`
- [ ] `make check` passes, including `tests/test_list_performance.py` and `test_dependency_check_parses_only_the_dependency` unchanged; each of the 15 tests in the migration decision asserts its new behaviour as described there; and the review note lists every existing test the branch changed, each with its old and new assertion, none deleted or weakened

## Notes

Planner, 2026-11-20: ticket rewritten as the read switch only. The lookup it builds on is `TASK-474`, `TASK-476`, `TASK-477`, `TASK-478` and `TASK-475`, and the runner claim change is `TASK-384`, all landing first. Earlier notes, including about 90 KB of pasted check output, are in Git history. Stays in `planning` until those are done; then compare this text with what landed, cold-read it, and move it to `todo`. Owner `human` keeps `chitty run` off it; start its worker by hand.

Owner `human` cleared 2026-11-20 at the owner's request: `TASK-384` removed the reason it was held back from `chitty run`. Earlier notes saying to start its worker by hand no longer apply. If a runner session cannot finish it, return it to `planning` to be split further.

The required conflict isolation and context-discovery wiring do not specify a workable interaction with autocommitted edits. `Repo._commit` calls `check.fix`, and `check.check` calls `repo.discovered_contexts()` even for a single changed path. The prescribed discovery reads every ticket via `source_copy`, which raises for the conflicting TASK-1; therefore editing unrelated TASK-2 cannot succeed as criterion 3 requires, even if `lookup` is isolated. The ticket also says `check.py` check and fix remain unchanged. A planner needs to decide how discovery avoids propagating unrelated source errors during this validation, including what it should do when the conflicted ticket may be the only source in an unconfigured context, and specify a regression fixture and assertions for that case. No implementation or tests were changed; the planned regressions and full verification remain outstanding.

Planning, 2026-11-20 (third read with serious findings since the latest rewrite, so split rather than patch). The `discovered_contexts` decision above stops source errors reaching discovery, but a cold read found it is not enough. Findings, each checked against `src/chitty/store.py` on this branch:

1. Discovery must call `ticket_ids()` itself, because `_invalidate` clears `_ticket_ids` and `_ticket_ref_files`.
2. `_collect_ticket_ids` raises on filename problems: `_files` raises on any `scan` problem, and a bad filename on `main` raises too. Reproduced: `chitty/backlog/notes.txt` makes `ticket_ids()` raise `task filename 'notes.txt' must end with .md`. Today `check` only reports this. Once discovery calls `ticket_ids()`, every autocommitted write would fail. Decide whether discovery reports filename problems or skips them.
3. `context_of` today loops over `tasks(context, "all")`, which would call `source_copy` on a conflicted ticket. It must call `source_copy(task_id)` directly.
4. `_tasks_in_location` calls `source_copy` for every ID, and so does every `tasks()` or `all_tasks()` caller on the write path: `new_id` on a ticket branch, `_delete_done`, `move` and `renumber`. While any ticket is conflicted, those writes (`add`, `archive`, `move`, `renumber`) raise. Decide whether they should fail or be isolated like `show` and `edit`.
5. Criterion 3's "(it fails before the discovery decision, through `check.fix`)" should become a mutant: it fails if `discovered_contexts` calls `source_copy`.

Suggested split: (a) tolerant ID and context collection: no raise on filename problems, and discovery from paths; (b) `context_of` and `lookup` through `source_copy` alone; (c) the listing switch, with a decision on conflicted tickets during multi-ticket writes; (d) test migrations. Check (d) against the one-ticket argument in Decisions.

Decided with the owner 2026-11-20, for the split: an operation fails only if it needs the conflicted ticket's content, and carries on if it needs only IDs or paths. Isolated: `add` (free IDs only), `move <ID>` and `archive <ID>` (fail only when `<ID>` is the conflicted ticket), and `show` and `edit` as already decided. Fail naming the conflicted ticket: `list`, `archive` with no ID (it needs every ticket's status) and `renumber` (it rewrites mentions in other tickets' text). Code that needs only IDs or paths uses `ticket_ids()` and paths; code that needs content uses `source_copy` one ID at a time. Bulk writes that check every ticket before writing come from `TASK-397`.

Planning 2026-11-20: rewritten as the single-ticket switch (piece B of the split); listing moved to `TASK-480`, context discovery to `TASK-479`. Former criterion 4 (history patched to raise) moved to `TASK-480`: `chitty show` lists children through `all_tasks()`, which still reads history until then.

This implementation is too large to finish in this session: it combines the single-ticket read switch, a new write-ownership rule, reference validation changes, a substantial real-Git CLI regression matrix with mutation checks, and migrations across multiple existing test suites. The ticket explicitly requires those migrations to land together with the switch, so committing a partial implementation would leave checks failing. The planner needs to split the work into independently verifiable stages or decide how to stage the migrations without breaking the suite. The branch was rebased onto main to obtain the landed dependencies; no implementation or tests were changed. Regression verification, mutation checks, formatting, and make check remain outstanding.

Too large to finish in this session: the read switch, write guard, reference validation, CLI regression and mutation matrix, and migrations must land together. A planner needs to split or stage these without breaking checks. No implementation or tests changed; all verification remains outstanding.

Planning 2026-11-21: split again after the worker found it too large. Moved out: the own-worktree write rule and former criterion 2 (`TASK-482`, lands first), and `Repo.exists` with the reference-isolation cases of criterion 3 (`TASK-483`, lands after). What remains: the single-ticket read switch, `StoredTask.branch` and `path`, criterion 1, the `show` cases of criterion 3, and the test migrations, which must land with the switch.

Planning 2026-11-21: the trimmed scope (read switch plus the named migrations) stays one ticket because the migrations cannot land apart from the switch. It runs only after `TASK-482`. If a session still cannot finish it, return it with the list of migrations done and left, and the owner will decide how to stage it.

Initial CLI regressions fail before the switch for conflict isolation, branch archive and dirty feature worktree. The branch-edit, retitle, unrelated-branch and malformed-copy cases currently pass before the switch and need stronger fixtures before they can prove their criteria.

Returning to planning: I could not finish the read switch and the coupled migrations in this session. The exploratory CLI tests showed pre-switch failures for archive path, conflict isolation and dirty feature worktree, but the other fixtures need strengthening to demonstrate failures; they were discarded rather than committed as incomplete regressions. No migrations were completed: all named migrations in tests/test_check_cross_branch_references.py, tests/test_next.py, tests/test_cli.py and tests/test_main_checkout_lock.py remain, along with any additional failures found by make check. No implementation changed. Full regression verification, fix, formatting and make check remain outstanding. The owner needs to decide how to stage the switch and migrations, as requested in the planning note.

Planner, 2026-11-21: all dependencies are `done`. Measured the switch with a spike (`ab2ac7bf` on `spike/task-378`): exactly 15 existing tests fail, each now listed with its migration; `context_of` must not parse; criterion 1 fixtures need `main`'s tickets dated after the branch edit, checked against `main` and the spike. Branch rebased onto `main`.

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
