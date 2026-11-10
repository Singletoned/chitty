---
title: "Plan guide: stub-first reds, fixed mutant lists, splitting crowded criteria"
status: doing
created: 2026-11-10
---

## Description

Four additions to the plan guide, `src/chitty/roles/plan.md`, from planning mullion. Each saves a repeat cold read or a worker mistake.

- When a ticket adds a module, have it say: first create the module with the names the tests import, each raising `NotImplementedError`, so each test fails on its own rather than all failing on one import error.
- Give each reader of a ticket the same fixed list of mutants (breaks the tests should catch), extended only with survivors you fixed. With fresh mutants on every read, every read found a fresh survivor and reads never converged.
- When one criterion collects more than about five separate checks (the same limit as criteria per ticket), split the ticket instead of growing the criterion.
- In the starting-point note, name the ticket's own paths to take from the ref (`git show <ref>:<path>`), because once dependencies land, `git diff <main-branch>...<ref>` also shows the reader's versions of them. This replaces the current bare `git diff` advice.

Keep each addition to one or two lines. Wording is the worker's choice; tests assert the phrases the worker writes, and the reviewer checks the meaning. Update `tests/test_guide_plan.py` for the starting-point change, dropping its `git diff <main-branch>...refs/cold-read/<ID>/<n>` and `configured main branch` phrases, and put the other tests in a new `tests/test_guide_plan_convergence.py` in the same style.

## Acceptance Criteria

- [ ] `guide("plan")` says tickets that add a module have the worker first create it with the imported names raising `NotImplementedError`.
- [ ] `guide("plan")` says to give every read of a ticket the same mutant list, extended only with survivors that were fixed.
- [ ] `guide("plan")` says the starting-point note names the ticket paths to take with `git show <ref>:<path>`, and no longer recommends `git diff <main-branch>...refs/cold-read/<ID>/<n>`.
- [ ] `guide("plan")` says to split a ticket when one criterion collects more than about five separate checks.

## Notes

Cold read 1 (Haiku): fixed: criterion 2 bundled two rules; split into criteria 2 and 4. Fixed: threshold named (about five checks); the `tests/test_guide_plan.py` phrases to drop are named. Rejected: pinning exact phrases in the ticket; wording is free and the reviewer checks meaning. Rejected: defining line length; one or two lines is a guide, not a test. Possible starting point: `git diff main...refs/cold-read/TASK-240/1`; check it against the current criteria, not trust it.

## History

- 2026-11-10T14:08:41Z jolly-heron → backlog
- 2026-11-10T14:18:48Z jolly-heron: changed description, acceptance criteria, notes
- 2026-11-10T14:18:51Z jolly-heron backlog → todo
- 2026-11-10T17:02:34Z open-newt todo → doing
