---
title: "Plan guide: stub-first reds, fixed mutant lists, splitting crowded criteria"
status: backlog
created: 2026-11-10
---

## Description

Four additions to the plan guide, `src/chitty/roles/plan.md`, from planning mullion. Each saves a repeat cold read or a worker mistake.

- When a ticket adds a module, have it say: first create the module with the names the tests import, each raising `NotImplementedError`, so each test fails on its own rather than all failing on one import error.
- Give each reader of a ticket the same fixed list of mutants (breaks the tests should catch), extended only with survivors you fixed. With fresh mutants on every read, every read found a fresh survivor and reads never converged.
- When a criterion collects more than a few separate checks, split the ticket instead of growing the criterion.
- In the starting-point note, name the ticket's own paths to take from the ref (`git show <ref>:<path>`), because once dependencies land, `git diff <main-branch>...<ref>` also shows the reader's versions of them. This replaces the current bare `git diff` advice.

Keep each addition to one or two lines. Update `tests/test_guide_plan.py` for the starting-point change, and put the other tests in a new `tests/test_guide_plan_convergence.py` in the same style.

## Acceptance Criteria

- [ ] `guide("plan")` says tickets that add a module have the worker first create it with the imported names raising `NotImplementedError`.
- [ ] `guide("plan")` says to give every read of a ticket the same mutant list, extended only with fixed survivors, and to split a ticket when one criterion collects more than a few checks.
- [ ] `guide("plan")` says the starting-point note names the ticket paths to take with `git show <ref>:<path>`, and no longer recommends `git diff <main-branch>...refs/cold-read/<ID>/<n>`.

## History

- 2026-11-10T14:08:41Z jolly-heron → backlog
