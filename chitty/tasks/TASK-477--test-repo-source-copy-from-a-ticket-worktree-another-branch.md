---
title: Test `Repo.source_copy` from a ticket worktree, another branch and outside Git
status: doing
depends_on:
  - TASK-476
parent: TASK-376
created: 2026-11-20
---

## Description

`TASK-476` adds `Repo.source_copy` in `src/chitty/store.py` and tests it only from the main checkout on `main`. This ticket adds tests from other checkouts: a ticket's own linked worktree, a non-ticket branch, and a directory outside Git. The behaviour already exists once `TASK-476` lands, so no new code is expected; if a test shows `source_copy` disagreeing with the rule below, fix `source_copy` and say so in the review note.

The rule (`docs/plan/ticket-state.md`, "Planning decisions", read with `git show plan/ticket-state:docs/plan/ticket-state.md`; implemented by `ticket_source` in `src/chitty/ticket_source.py`): a checkout on a ticket's own branch reads that ticket from its working tree; a checkout on any other non-`main` branch reads tickets without a ticket branch from `main`'s tip; outside Git, everything is read from the working tree.

Because the code exists, each test must be shown to catch a wrong version. Commit these mutants as tests, in the style of `tests/test_property_blockers.py` (`TestBlockerPropertyMutants`): each applies the wrong version with `unittest.mock.patch`, runs the same check, and asserts it fails: `assertRaises(AssertionError)` for mutants 1 and 2, and for mutant 3 `assertRaisesRegex(ChittyError, "refs/heads/main")`, the Git error it hits outside a repository. Each mutant is a `with unittest.mock.patch(...)` block around the same check helper the positive test uses; a wrapper captures the real function before patching, so it does not call itself. The landed code calls `ticket_source` from `Repo._choose_source` through the name `chitty.store.ticket_source`, so patch that name. The wrong versions: (1) `chitty.store.ticket_source` replaced by a wrapper that returns `WORKING_TREE` whenever the real one returns anything else, against the `TASK-7` and `feature` checks of criterion 1; (2) a wrapper that passes `None` as the third argument (`current_branch`) to the real one, against the `TASK-5` check; (3) `chitty.store.git.is_repository` patched to return `True`, against the outside-Git check of criterion 2.

Recording `chitty.git` calls, wherever a criterion asks for it: wrap each public function in `chitty.git` and record only outermost calls; a call made while another wrapped `chitty.git` function is running (such as the helper `git.is_repository` calls itself) is not recorded.

Tests: a new `tests/test_source_copy_checkouts.py`, set up as `tests/test_source_copy.py` from `TASK-476` is. Make the linked worktree with `git worktree add .worktrees/task-5 -b task-5`. No property: a fixed set of checkouts; the generated property is `TASK-393`.

## Acceptance Criteria

- [ ] With `TASK-5` and `TASK-7` committed on `main` with title `main`: in the linked worktree of `task-5`, after a commit there retitling `TASK-5` to `branch`, `TASK-5` gives `ref` `None` and a further uncommitted retitle made there; `TASK-7` (no branch) gives `ref` `main` and title `main` despite an uncommitted retitle in that worktree. In a checkout on branch `feature`, `TASK-7` gives `ref` `main` and title `main` despite an uncommitted retitle there. Compare `copy.ref` and `copy.task.frontmatter.title`
- [ ] Outside a Git repository, `source_copy` gives `ref` `None` and the working-tree copy, and, with every `chitty.git` function wrapped to record calls from after `Repo.open` returns, calls none except `git.is_repository`
- [ ] Each of the three mutants in the Description is committed as a test that asserts the matching check fails against it; `make check` passes

## Plan

Create checkout fixtures and shared source-copy checks for the linked worktree, feature branch, and non-Git directory. Exercise each check against the specified patched mutants, including outermost Git-call recording, then run formatting and checks and hand off.

## History

- 2026-11-20T17:43:41Z jolly-dusky-badger → planning
- 2026-11-20T19:05:57Z jolly-dusky-badger: changed description
- 2026-11-20T20:05:25Z jolly-dusky-badger: changed description
- 2026-11-20T20:05:25Z jolly-dusky-badger planning → cold-read
- 2026-11-20T20:07:06Z jolly-dusky-badger: changed description, acceptance criteria
- 2026-11-20T20:07:06Z jolly-dusky-badger cold-read → todo
- 2026-11-20T20:11:50Z friendly-zinc-gannet todo → doing
- 2026-11-20T20:13:47Z friendly-zinc-gannet: wrote the plan
