---
title: Make cold reads a read-only scan
status: planning
created: 2026-11-16
---

## Description

Retro of 2026-11-16: cold-read tickets passed their first review no more often than others (69% against 73%; since 2026-11-05, 69% against 79%), and the implementing read costs an extra agent session, repeated until a read finds nothing.

Make a cold read one read-only pass. A fresh agent on a cheap model, close to the one that will do the work, reads the ticket and the code and documents it names, and reports. It makes no worktree, branch, ref, commit or file change, and runs no Chitty writes; it may run commands that change no files, such as `git grep` or existing code on a case it doubts. Every ticket gets one read; there is no repeat-until-clean and no separate stronger-model read for tickets with nothing to run.

The planner keeps the sufficiency read, done on the ticket text, the referenced code and the reader report. The fixed mutant list goes: without an implementation nothing runs it. Proving that tests fail without the change moves to the runner (`TASK-338`, not part of this ticket). Problems a read misses come back through the existing return to planning (`TASK-323`): the guides say plainly that this is the expected route, not a failure.

Files: `src/chitty/roles/cold-read.md`, the cold-read bullets of `src/chitty/roles/plan.md`, the Cold read section of `docs/plan/pipeline-and-feedback.md`, and the guide tests that assert the old procedure (`tests/test_guide_cold_read.py`, `tests/test_guide_cold_read_mutants.py`, `tests/test_guide_plan.py`, `tests/test_guide_plan_convergence.py`, and any other `tests/test_guide_*.py` that `make check` shows asserting removed text). Update or delete those tests; do not keep old guide text to satisfy them. Put new tests in `tests/test_guide_read_only_cold_read.py`.

Out of scope: removing the `refs/cold-read` filtering in `src/chitty/git.py` and existing refs (`TASK-337`), and the planning-return wording in `work.md` and `review.md` (`TASK-354` and the return-scope ticket).

No property tests: this is fixed guide text with no input. Phrase checks on the rendered guides are the tests.

## Acceptance Criteria

- [ ] The rendered `chitty guide cold-read` describes the read-only pass above and contains none of these phrases: `git worktree add`, `git update-ref`, `implement it`, `apply each mutant`, `Surviving mutants`, `failed before the fix`. Its report still asks for done meaning, the files a worker would change, ambiguities and open decisions, missed properties, unverified behaviour and unhandled states, wrong claims, and for each finding a file and line and the exact ticket wording to change. A test in `tests/test_guide_read_only_cold_read.py` checks both the absences and the kept report items, and fails before the change.
- [ ] The rendered `chitty guide plan` asks for one read-only cold read of every ticket by a fresh agent on a cheap model close to the worker; keeps the sufficiency read on ticket text, referenced code and report; keeps the `NotImplementedError` advice for new modules; says that problems a read misses return through planning from work or review, as the expected route. It contains none of: `same fixed list of mutants`, `A read that only probed`, `until a read finds none`, `stronger model reads the ticket`, `refs/cold-read`, `possible starting point`. Tested in the same file; the test fails before the change.
- [ ] The Cold read section of `docs/plan/pipeline-and-feedback.md` describes the same procedure and no longer mentions implementing reads, the mutant list or `refs/cold-read`. Old-procedure guide tests are updated or deleted, not satisfied by keeping old text. `make check` passes.

## History

- 2026-11-16T09:50:16Z intrepid-coral-raven → backlog
- 2026-11-16T09:59:48Z intrepid-coral-raven: changed description
- 2026-11-16T10:38:24Z intrepid-coral-raven backlog → planning
- 2026-11-16T12:50:12Z open-russet-eel: changed description, acceptance criteria
