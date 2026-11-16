---
title: Make cold reads a read-only scan
status: review
created: 2026-11-16
---

## Description

Retro of 2026-11-16: cold-read tickets passed their first review no more often than others (69% against 73%; since 2026-11-05, 69% against 79%), and the implementing read costs an extra agent session, repeated until a read finds nothing.

Make a cold read one read-only pass. A fresh agent on a cheap model, close to the one that will do the work, reads the ticket and the code and documents it names, and reports. It makes no worktree, branch, ref, commit or file change, and runs no Chitty writes; `git status` in the checkout is the same before and after. It may still try behaviour rather than assume, with commands that leave `git status` unchanged, such as `git grep` or running existing code on a case it doubts. Every ticket gets one read. The planner does not repeat the read after fixing findings, and there is no separate stronger-model read for tickets with nothing to run. The existing optional fresh stronger reader, for uncertainty or repeated work–review failures, stays.

The planner keeps the sufficiency read, done on the ticket text, the referenced code and the reader report. The fixed mutant list goes: without an implementation nothing runs it. The plan guide keeps its advice to say which test must fail without the fix, until the runner proves it (`TASK-338`, not part of this ticket). Problems a read misses come back through the existing return to planning (`TASK-323`): the plan guide says plainly that this is the expected route, not a failure.

Files:
- `src/chitty/roles/cold-read.md` (rewrite the procedure and the report list).
- `src/chitty/roles/plan.md`: the bullets on mutants, `Cold-read every ticket`, the sufficiency read, `A read that only probed`, and starting the reader (keeping refs and starting-point notes).
- The Cold read section of `docs/plan/pipeline-and-feedback.md`.
- Tests that assert removed text. `make check` does not catch a stale assertion that still passes, so all are named: `tests/test_guide_cold_read.py`, `tests/test_guide_cold_read_mutants.py`, `tests/test_guide_cold_read_sufficiency.py`, `tests/test_guide_cold_read_reports.py`, `tests/test_guide_cold_read_notes.py`, `tests/test_guide_plan.py`, `tests/test_guide_plan_convergence.py`, and `TestGuide` in `tests/test_cli.py` (`test_plan_guide_describes_implementing_cold_reads`, `test_plan_guide_requires_repeat_reads_and_decision_tests`). Update or delete each assertion; no test may require text this ticket removes.
- New tests go in `tests/test_guide_read_only_cold_read.py`. All checks use text flattened with `" ".join(text.split())`.

Out of scope: removing the `refs/cold-read` filtering in `src/chitty/git.py` and existing refs (`TASK-337`), and the planning-return wording in `work.md` and `review.md` (`TASK-360`, `TASK-354`).

No property tests: this is fixed guide text with no input. Phrase checks on the rendered guides and the design file are the tests.

## Acceptance Criteria

- [x] Flattened `guide("cold-read")` contains `Run no Chitty writes`, `no worktree, branch, ref, commit or file change`, `Try behaviour rather than assume`, and the report items `What done means`, `would change`, `Ambiguities`, `Missed properties`, `Unverified behaviour`, `Wrong claims` and `the exact wording to change`. It contains none of: `worktree add`, `worktree remove`, `update-ref`, `refs/cold-read`, `implement it`, `Implement the simplest`, `mutant`, `failed before the fix`, `UV_PROJECT_ENVIRONMENT`, `Commit your work`, `nothing to run`. A test in `tests/test_guide_read_only_cold_read.py` checks each phrase as a subtest and fails before the change.
- [x] Flattened `guide("plan")` contains `one read-only cold read`, `cheap model`, `expected route`, `NotImplementedError`, `a plausible minimal implementation` and `must fail without the fix`, and none of: `mutant`, `A read that only probed`, `until a read finds none`, `Repeat the cold read`, `implementing`, `throwaway worktree`, `with and without the fix`, `refs/cold-read`, `possible starting point`. Tested in `tests/test_guide_read_only_cold_read.py`; the test fails before the change.
- [x] The Cold read section of `docs/plan/pipeline-and-feedback.md` (from `## Cold read` to the next `##`) contains `read-only` and none of `refs/cold-read`, `mutant`, `worktree`, `implementing`; tested in the same file. No assertion in `tests/` requires text this ticket removes. `make check` passes.

## Plan

Rewrite the cold-read and plan guides plus the pipeline design section to describe one read-only pass, preserving the planner sufficiency read and existing optional stronger reader. Update the specifically named guide tests and add tests/test_guide_read_only_cold_read.py with flattened phrase assertions. First run the new focused test against current text to confirm it fails, then implement, format/check, inspect status and diff, commit implementation files with Task: TASK-336, and verify every criterion before recording the ticket note and moving to review.

## Notes

Verification: the new read-only guide test failed before the guide rewrite (24 failures, including forbidden legacy phrases); after the fix, `make check` passed with `Ran 577 tests in 19.721s` and `OK`. `chitty fix` reported only pre-existing warnings in unrelated task files and made no changes. The full suite emits an expected fixture error about incomplete `autocommit` configuration, but the suite still passes.

## Summary

Implemented one read-only cold read across the cold-read and plan guides and pipeline design, with updated phrase tests and new regression coverage. Handoff: review commit `989a26a`. Verification: `make format && make check` passes; working tree is clean. Follow-up: none.

## History

- 2026-11-16T09:50:16Z intrepid-coral-raven → backlog
- 2026-11-16T09:59:48Z intrepid-coral-raven: changed description
- 2026-11-16T10:38:24Z intrepid-coral-raven backlog → planning
- 2026-11-16T12:50:12Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T12:51:12Z open-russet-eel: changed owner
- 2026-11-16T12:51:12Z open-russet-eel planning → cold-read
- 2026-11-16T12:54:30Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T12:54:30Z open-russet-eel cold-read → planning
- 2026-11-16T12:54:40Z open-russet-eel: changed owner
- 2026-11-16T12:54:40Z open-russet-eel planning → todo
- 2026-11-16T12:55:40Z tidy-white-kestrel todo → doing
- 2026-11-16T12:55:53Z tidy-white-kestrel: wrote the plan
- 2026-11-16T13:01:25Z tidy-white-kestrel: changed notes, summary; ticked acceptance criteria
- 2026-11-16T13:01:25Z tidy-white-kestrel doing → review
