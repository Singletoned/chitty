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

- [x] `guide("plan")` says tickets that add a module have the worker first create it with the imported names raising `NotImplementedError`.
- [x] `guide("plan")` says to give every read of a ticket the same mutant list, extended only with survivors that were fixed.
- [x] `guide("plan")` says the starting-point note names the ticket paths to take with `git show <ref>:<path>`, and no longer recommends `git diff <main-branch>...refs/cold-read/<ID>/<n>`.
- [x] `guide("plan")` says to split a ticket when one criterion collects more than about five separate checks.

## Plan

Update the planning role with the four requested instructions, revise the existing starting-point guide test, and add focused convergence tests in tests/test_guide_plan_convergence.py. Run the new tests against the current guide first to confirm they fail, then implement and verify with make format and make check.

## Notes

Cold read 1 (Haiku): fixed: criterion 2 bundled two rules; split into criteria 2 and 4. Fixed: threshold named (about five checks); the `tests/test_guide_plan.py` phrases to drop are named. Rejected: pinning exact phrases in the ticket; wording is free and the reviewer checks meaning. Rejected: defining line length; one or two lines is a guide, not a test. Possible starting point: `git diff main...refs/cold-read/TASK-240/1`; check it against the current criteria, not trust it.

New guide tests failed against the original guide before implementation. Full make format && make check passed after correcting an assertion wording mismatch.

Review failed (tests): The stub instruction tells the planner to create the module during a cold read, not to have the ticket instruct its worker to create the stubs first. Make the guide explicitly require that ticket instruction and test that meaning. `chitty guide plan` printed: "Cold-read every ticket, even a small one. If it adds a module, first create it with the names the tests import, each raising `NotImplementedError`". `make format && make check` passed, including 427 Python tests and the Node tests, but the phrase assertions do not exercise who must create the stubs.

1: fail - The guide does not tell planners to put the stub-first instruction in the ticket for the worker.
2: pass - The guide specifies the fixed mutant list and fixed survivors.
3: pass - The guide names ticket paths and `git show <ref>:<path>` without the old diff advice.
4: pass - The guide specifies splitting at more than about five checks.

Review finding addressed: the guide now tells the ticket author to require its worker to create importable stubs first. Strengthened the regression test; it failed before the guide change. An initial assertion phrase did not match the guide wording, corrected the assertion before rerunning checks.

## Summary

Implemented the requested planning-guide guidance and tests. Verified with make format && make check; regression tests were confirmed failing against the original guide. No known follow-ups.

## History

- 2026-11-10T14:08:41Z jolly-heron → backlog
- 2026-11-10T14:18:48Z jolly-heron: changed description, acceptance criteria, notes
- 2026-11-10T14:18:51Z jolly-heron backlog → todo
- 2026-11-10T17:02:34Z open-newt todo → doing
- 2026-11-10T17:02:53Z open-newt: wrote the plan
- 2026-11-10T17:04:49Z open-newt: changed notes; ticked acceptance criteria
- 2026-11-10T17:04:54Z open-newt: changed summary
- 2026-11-10T17:04:54Z open-newt doing → review
- 2026-11-10T17:53:39Z rosy-zander: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-10T17:53:39Z rosy-zander review → doing
- 2026-11-10T18:00:46Z rosy-toad: changed notes; ticked acceptance criteria
