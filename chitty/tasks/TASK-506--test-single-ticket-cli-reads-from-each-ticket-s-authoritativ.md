---
title: Test single-ticket CLI reads from each ticket's authoritative source
status: doing
priority: high
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-21
---

## Description

Split from `TASK-378` on 2026-11-21, because three workers found that ticket too large for one session. `TASK-378` switches single-ticket reads (`lookup`, `find`, `context_of`, so `chitty show`, `edit`, `note`) to `Repo.source_copy`. This ticket adds the CLI tests that show the switch is wired through, so it starts after `TASK-378` lands. Read `TASK-378`'s Decisions for the behaviour these cases check.

Tests: real-Git CLI tests in a new `tests/test_ticket_reads.py`, inheriting `CliTestCase` from `tests/test_cli.py`, set up as `tests/test_check_cross_branch_references.py` does. `make check` takes about a minute here; run it with a shell timeout of at least five minutes. The merged-branch rule is already tested by `tests/test_source_copy.py` (`test_merged_then_main_changed`); the `has no tip` error is tested by a separate ticket, not here. Record in a note, for each case of criteria 1 and 2, how it fails on the commit before the switch (see below). Each criterion 1 fixture commits `main`'s tickets with `GIT_COMMITTER_DATE=2030-01-01T00:00:00Z` before the ticket branch is made, so today's newest-commit rule prefers `main`'s copy; without that date the branch-edit and retitle cases pass before the change. Checked 2026-11-21 against `main` and the spike: on `main` the branch edit shows `main`'s title, the retitle shows `main`'s path, the branch archive fails with `used by more than one file`, the `feature`-only ticket is shown, and the malformed branch copy shows `main`'s copy; with the spike each gives the criterion's result. No property: a fixed set of cases, each in the criteria; the generated property over placements is `TASK-393`.

The commit before the switch: the parent of the oldest commit on `main` that has the trailer `Task: TASK-378` and changes `src/chitty/store.py`, that is `git log --format=%H --grep='^Task: TASK-378$' main -- src/chitty/store.py | tail -1` followed by `^`. It returns nothing until `TASK-378` lands; landed work commits carry the trailer (for example `git log --format=%h --grep='^Task: TASK-426$' main -- src/chitty/run.py` prints `5bae8473`).

Error cases: every "fails" means the CLI exits 1 with the error text in `result.stderr`, as `tests/test_check_cross_branch_references.py` checks. The `task-1:<path>: <error>` prefix already exists: `Repo._parse_source_copy` formats it. To show a case fails there, stay in this ticket's own worktree (do not create another): `git show <commit>:src/chitty/store.py > src/chitty/store.py`, run `python -m unittest tests.test_ticket_reads`, record the failures, then `git checkout -- src/chitty/store.py`. The switch is confined to `src/chitty/store.py`, so restoring that one file is enough; check `git diff <commit> main -- src` names only that file before relying on it.

Out of scope: any change to `src/`. If a case fails after the switch, the switch is wrong: return this ticket to `planning` naming the case.

## Acceptance Criteria

- [ ] From the main checkout, through the CLI, with `main`'s tickets committed dated `2030-01-01T00:00:00Z` before each branch is made (see Tests): `chitty show` of a ticket edited on `task-<n>` prints the branch copy and `branch: task-<n>`; of a ticket retitled on `task-<n>`, prints a `path:` line ending in the branch file name; of a ticket archived on its branch, prints a `path:` line ending in `chitty/tasks/archive/<its file name>`; of a ticket only on branch `feature`, fails with an error starting `no task TASK-<n>` (each fails on the commit before the switch). Guard, passing before and after: of a provisional `TASK-K7Q2MX` committed only on branch `task-k7q2mx`, prints that copy and `branch: task-k7q2mx`
- [ ] With `TASK-1` edited on both `task-1` and `main` since they split, and `TASK-2` only on `main`, referencing no other ticket: `chitty show TASK-2` and `chitty edit TASK-2 --note x` succeed; `chitty show TASK-1` fails with the error containing `changed on both` and naming `task-1` and `main` (fails on the commit before the switch). With a file not starting with `---` committed as `TASK-1` on `task-1`, `chitty show TASK-1` fails with `task-1:<its relative path>: file must start with '---' frontmatter`, and `Repo.context_of(TaskId.parse("TASK-1")).name` is `tasks` without raising (it raises on the commit before the switch). With `TASK-1` committed valid on `main` and edited (title `branch`) on `task-1`, and the main checkout's `TASK-1` file then overwritten, uncommitted, with `not frontmatter`: from the main checkout `Repo.context_of(TaskId.parse("TASK-1")).name` is `tasks` and `Repo.open(root).find(TaskId.parse("TASK-1")).task.frontmatter.title` is `branch` (not `chitty show`, whose child listing goes through `all_tasks()` and is `TASK-480`) (both raise the working-tree parse error on the commit before the switch). In a linked worktree on branch `feature`, an uncommitted retitle of `TASK-2` there is not shown: `chitty show TASK-2` prints the title committed on `main`
- [ ] `make check` passes, `git diff main...HEAD --stat` touches only `tests/test_ticket_reads.py` and this ticket, and a note records each case's failure on the commit before the switch

## Plan

Add isolated real-Git CLI fixtures for each specified source-read case, verify the regression cases against the pre-switch store, then restore it and run fix, format and the full check.

## Notes

The post-switch malformed main working-tree case fails: `Repo.context_of` returns `tasks`, but `chitty show TASK-1` exits 1 with the working-tree frontmatter error instead of showing the branch title. `show` calls `repo.all_tasks()` to find children after `find`, which parses the malformed working copy. The ticket explicitly puts `src/` changes out of scope and requires return to planning if a post-switch case fails. Decide how to fix or separate that behavior before this test can pass. The CLI wraps errors in `Error: `, so the unrelated-branch assertion checks that prefix followed by `no task TASK-3`.

Partial tests are committed. `make check` ran 914 tests: the malformed working-tree show case was the only failure; ruff and pyright passed. With the parent of the oldest TASK-378 store commit substituted (the src diff to main names only store.py), the pre-switch tests failed as follows: branch edit showed main title; retitle showed main path; archive reported duplicate files; feature-only ticket was shown; conflicted ticket showed main instead of error; malformed branch showed main instead of error; malformed main working tree raised during context lookup; linked feature worktree showed the uncommitted title. Provisional guard passed. The malformed branch context assertion and malformed main show assertion were not independently reached in that run; their separate pre-switch evidence remains to be collected. Restored store.py. Full passing verification and review handoff remain unfinished.

Planner 2026-11-21: `chitty show` also lists the ticket's children through `repo.all_tasks()` (`src/chitty/cli.py:604`), which parses every working-tree copy. That is a listing, so it belongs to `TASK-480`, not here. Criterion 2's malformed main working-tree case now asserts `Repo.find` instead of `chitty show`, and the `chitty show` case is recorded on `TASK-480`. Put each case of criteria 1 and 2 in its own test method, so the pre-switch run reaches every assertion independently. The malformed-branch `context_of` assertion and the malformed main working-tree `find` assertion each need their own pre-switch failure in the note.

## History

- 2026-11-21T11:40:32Z sunny-ebony-kestrel → planning
- 2026-11-21T11:42:58Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T11:43:51Z sunny-ebony-kestrel: changed description
- 2026-11-21T11:43:51Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T11:49:04Z sunny-ebony-kestrel: changed description
- 2026-11-21T12:37:29Z calm-quartz-stoat todo → doing
- 2026-11-21T12:39:24Z calm-quartz-stoat: wrote the plan
- 2026-11-21T12:41:58Z calm-quartz-stoat: changed owner, notes
- 2026-11-21T12:41:58Z calm-quartz-stoat doing → planning
- 2026-11-21T12:43:15Z sunny-ebony-kestrel: changed acceptance criteria, notes
- 2026-11-21T12:43:15Z sunny-ebony-kestrel planning → todo
- 2026-11-21T12:48:19Z daring-ochre-newt todo → doing
