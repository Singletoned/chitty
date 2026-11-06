---
title: Repeat cold reads after fixes, and compare decisions with criteria
status: done
priority: medium
depends_on:
  - TASK-194
parent: TASK-106
created: 2026-11-05
---

## Description

Second part of the `echonomicon` suggestion in `TASK-194`. Fixes to a ticket are a source of new faults. There, three fixed tickets sampled at random for a second read all had real problems, two making the check command impossible to pass, and later reads found faults the first fixes had introduced, such as a criterion left contradicting an updated description. Here, the second read of the `TASK-190` split on 2026-11-05 found two serious faults. Also there, the first ticket done by the weaker model was correct but left stated decisions untested, because implementers test what criteria name.

Add these bullets to `src/chitty/roles/plan.md`, straight after the bullets on cold reads that `TASK-194` leaves, adjusting only line wrapping:

"Repeat the cold read after fixing a serious finding, until a read finds none: fixes are a source of new faults."

"Compare each decision in the description with the criteria, because workers test what criteria name. Say which test must fail without the fix, because a nearby test may already pass."

Those bullets ship to every repository, so do not name `make`. `src/chitty/roles/plan.md` does not reach `AGENTS.md`, so no `chitty init` or version bump is needed. Whichever of this and `TASK-188` lands second merges the wording.

## Acceptance Criteria

- [x] A test in `TestGuide` in `tests/test_cli.py`, collapsing whitespace in `guide("plan")` first so that line wrapping cannot break it, shows it containing `until a read finds none`, `what criteria name` and `must fail without the fix`, and fails against the current `plan.md`

## Plan

Add a TestGuide regression test that normalizes whitespace in guide("plan") and asserts the three required phrases. Add the two prescribed bullets to src/chitty/roles/plan.md immediately after the existing cold-read bullets, changing only line wrapping. Run the focused test before and after the guide change, then make format && make check.

## Notes

Implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-195/1`. Fixed: a test on exact phrases broke on line wrapping in my own wording, as on `TASK-194` and `TASK-196`; and where the bullets go. Rejected: depending on `TASK-188`, which neither needs the other, and a merge handles the order; overlap with `TASK-196`, since this tells planners what to write and that tells workers what to do; and checking position in the test, which the reviewer can read.

Second implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-195/2`: nothing serious. The test failed on all three phrases without the change and passed with it, and `make check` passed. Rejected: naming a position in the current `plan.md`, because this depends on `TASK-194`, whose bullets will be there when this starts; and checking position in the test, as before.

The ticket says no version bump is needed, but `make check` enforces a bump for every `src/chitty/roles` change via `check_version_bump.py`; bumped `__version__` to `0.1.39` so the required check passes.

Verified the new regression test failed before the guide bullets were added (all three phrases missing), then passed after the fix. `make format && make check` passed.

Reviewed: verified the prescribed planning bullets and whitespace-normalized TestGuide regression test; the baseline main guide lacks all three required phrases, and make format && make check passes.
1: pass - implementation and verification satisfy the criterion.

## Summary

Implemented the two planning-role bullets and a whitespace-normalized `TestGuide` regression test covering all required phrases. Bumped `__version__` to `0.1.39` because `make check` requires version bumps for `src/chitty/roles` changes. Focused regression test failed before the guide fix and passed after it; `make format && make check` passes. No follow-ups.

## History

- 2026-11-05T17:53:54Z mellow-newt → backlog
- 2026-11-05T18:03:37Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T18:03:38Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T18:03:38Z mellow-newt backlog → todo
- 2026-11-05T18:13:36Z mellow-newt todo → backlog
- 2026-11-05T18:18:04Z mellow-newt: changed notes
- 2026-11-05T18:18:05Z mellow-newt backlog → todo
- 2026-11-06T20:22:49Z rosy-heron todo → doing
- 2026-11-06T20:23:56Z rosy-heron: wrote the plan
- 2026-11-06T20:24:06Z rosy-heron: wrote the plan
- 2026-11-06T20:25:14Z rosy-heron: changed notes
- 2026-11-06T20:26:57Z rosy-heron: changed notes, summary; ticked acceptance criteria
- 2026-11-06T20:26:57Z rosy-heron doing → review
- 2026-11-06T20:29:48Z upbeat-raven: changed notes; ticked acceptance criteria
- 2026-11-06T20:29:48Z upbeat-raven review → done
