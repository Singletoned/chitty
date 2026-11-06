---
title: Tell workers to see a regression test fail, and to stop on a wrong ticket
status: done
priority: medium
parent: TASK-106
created: 2026-11-05
---

## Description

Some faults only show up in the real implementation, however the ticket was read. On `TASK-31` in `echonomicon` a test passed with or without the fix, and on `TASK-137` here a cheap model left out a test, which `TASK-182` now adds. `src/chitty/roles/work.md` says nothing about either. The human agreed on 2026-11-05 to add this to the guide alongside implementing cold reads, which do not replace it.

Add this bullet to `src/chitty/roles/work.md`, adjusting only line wrapping:

"When a ticket asks for a regression test, see it fail without the fix, by running it before you write the fix or with the fix reverted, and say so in a note. If it passes without the fix, it proves nothing: change the test until it fails without the fix. If the ticket itself is wrong, because following it would break something or a claim in it is false, do not work around it. That is a person's decision, however cheap the fix looks: note what you found and set `-s blocked`. An unclear detail with a cheap default is not this: choose it, as below."

Put it before the bullet on cheap-to-reverse defaults, so that "as below" holds. This file ships to every repository, so do not name `make`. `chitty guide work` serves it at run time, and `AGENTS.md` does not hold it, so no `chitty init` or version bump is needed. Other tickets edit this file, including `TASK-173` and `TASK-179`, so add only this bullet.

Out of scope: having Chitty check that a test failed.

## Acceptance Criteria

- [x] A test in `TestGuide` in `tests/test_cli.py`, collapsing whitespace in `guide("work")` first so that line wrapping cannot break it, shows it containing `see it fail without the fix`, `change the test until it fails without the fix`, `do not work around it`, `a person's decision` and `An unclear detail with a cheap default is not this`, and fails against the current `work.md`

## Plan

Add the requested regression-test and wrong-ticket guidance bullet to src/chitty/roles/work.md immediately before the cheap-defaults bullet. Extend TestGuide in tests/test_cli.py to collapse guide whitespace and assert the required phrases. Run the test against the current guide first to confirm failure, then implement, run focused tests and make check, tick the criterion, run chitty fix, summarize, and set review.

## Notes

Implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-196/1`. Fixed: a test on exact phrases broke on line wrapping in my own wording; "change it" did not say what to change; when to run the test, and what happens on a ticket with no regression test; and the `TASK-137` claim, which that ticket's own text cannot confirm, now points at `TASK-182`. Checked: `TASK-173` and `TASK-179` do name `work.md`. Rejected: requiring a position or a bullet in the test, because the description says where it goes and the reviewer can read it.

Second implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-196/2`. Fixed: serious, a wrong ticket that was cheap to fix was caught between "set `-s blocked`" and the existing "Block only for a costly reversal or a person decision", so the bullet now calls it a person's decision; "change the test" could have meant weakening it; and `Luna` meant nothing in this repository. Rejected: checking the bullet's position in the test, which the reviewer can read. A third read follows, since a serious finding was fixed.

Third implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-196/3`: nothing serious. The test failed on all five phrases without the change and passed with it, and `make check` exited 0. Rejected: the `TASK-137` attribution to a cheap model, which the planning session saw directly though the tickets do not say it; a test made to fail for an unrelated reason, and pasted phrases, which are for the reviewer; a regression test that cannot be run, which the existing bullet on being blocked covers; and overlap with "Block only for a costly reversal or a person decision", since the new bullet names this as a person's decision.

Owner set to human only so `chitty run` skips it while a separate reviewer reviews it; cleared by that review.

Reviewed: criterion 1 met. TestGuide test collapses whitespace in guide('work') and asserts all five phrases; bullet in work.md matches ticket text, sits before the cheap-defaults bullet, does not name make, only that bullet added. Regression run recorded in ticket (failed before, passes after). make check passes.

## Summary

Added the regression-test failure and wrong-ticket blocking guidance before the cheap-defaults bullet, plus a whitespace-collapsed TestGuide regression test covering all required phrases. Verified the new test failed before the guide change, then passed after it; TestGuide and make check passed (including 278 Python tests and Node tests). chitty fix completed with only pre-existing Markdown delimiter warnings in other tickets.

## History

- 2026-11-05T17:53:54Z mellow-newt → backlog
- 2026-11-05T17:59:51Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T17:59:52Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T17:59:52Z mellow-newt backlog → todo
- 2026-11-05T18:13:37Z mellow-newt todo → backlog
- 2026-11-05T18:18:34Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T18:18:35Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T18:22:07Z mellow-newt: changed notes
- 2026-11-05T18:22:08Z mellow-newt backlog → todo
- 2026-11-06T00:14:05Z witty-kestrel todo → doing
- 2026-11-06T00:14:20Z witty-kestrel: wrote the plan
- 2026-11-06T00:20:13Z witty-kestrel: ticked acceptance criteria
- 2026-11-06T00:20:22Z witty-kestrel: changed summary
- 2026-11-06T00:20:23Z witty-kestrel doing → review
- 2026-11-06T10:00:10Z youthful-toad: changed owner, notes
- 2026-11-06T10:06:00Z youthful-toad: changed owner, notes; overrode review independence
- 2026-11-06T10:06:00Z youthful-toad review → done
- 2026-11-06T16:46:11Z jolly-quail done → archived
