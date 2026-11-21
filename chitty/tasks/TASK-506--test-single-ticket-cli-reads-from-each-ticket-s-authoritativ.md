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
- [ ] With `TASK-1` edited on both `task-1` and `main` since they split, and `TASK-2` only on `main`, referencing no other ticket: `chitty show TASK-2` and `chitty edit TASK-2 --note x` succeed; `chitty show TASK-1` fails with the error containing `changed on both` and naming `task-1` and `main` (fails on the commit before the switch). With a file not starting with `---` committed as `TASK-1` on `task-1`, `chitty show TASK-1` fails with `task-1:<its relative path>: file must start with '---' frontmatter`, and `Repo.context_of(TaskId.parse("TASK-1")).name` is `tasks` without raising (it raises on the commit before the switch). With `TASK-1` committed valid on `main` and edited (title `branch`) on `task-1`, and the main checkout's `TASK-1` file then overwritten, uncommitted, with `not frontmatter`: from the main checkout `Repo.context_of(TaskId.parse("TASK-1")).name` is `tasks` and `chitty show TASK-1` prints title `branch` (both raise the working-tree parse error on the commit before the switch). In a linked worktree on branch `feature`, an uncommitted retitle of `TASK-2` there is not shown: `chitty show TASK-2` prints the title committed on `main`
- [ ] `make check` passes, `git diff main...HEAD --stat` touches only `tests/test_ticket_reads.py` and this ticket, and a note records each case's failure on the commit before the switch

## Plan

Add isolated real-Git CLI fixtures for each specified source-read case, verify the regression cases against the pre-switch store, then restore it and run fix, format and the full check.

## History

- 2026-11-21T11:40:32Z sunny-ebony-kestrel → planning
- 2026-11-21T11:42:58Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T11:43:51Z sunny-ebony-kestrel: changed description
- 2026-11-21T11:43:51Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T11:49:04Z sunny-ebony-kestrel: changed description
- 2026-11-21T12:37:29Z calm-quartz-stoat todo → doing
- 2026-11-21T12:39:24Z calm-quartz-stoat: wrote the plan
