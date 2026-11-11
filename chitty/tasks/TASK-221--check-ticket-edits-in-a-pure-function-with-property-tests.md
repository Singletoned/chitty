---
title: Check ticket edits in a pure function, with property tests
status: done
labels:
  - spec-first
priority: medium
created: 2026-11-06
---

## Description

`chitty run` is tested almost only through real Git repositories, worktrees and fake-agent processes, about 150 of `make check`'s 290 seconds. Even so, on 2026-11-06 those tests missed bugs that came from ticket states their fixtures never built. One of them: `_fail_review` moving a ticket with criteria `review → doing` was refused for missing verdict lines (`TASK-206`).

The human wants to move towards pure decision functions tested with property-based tests, and to run the real-Git runs only as a few smoke tests before landing. This ticket is the first, small slice, and a candidate for the spec-first pilot (`TASK-109`).

1. **A pure function.** Move the checks in `Repo.edit` (`src/chitty/store.py`, from "nothing to change" through `_validate_review_verdict`, the independence check and `_escalate_repeated_failure`) into a pure `check_edit(task, edit, reviewer) -> Edit`. It returns the edit to apply, after escalation, or raises `ChittyError` with today's messages.
   - It reads no files, no Git and no environment. `Repo.edit` calls it with `actor()` passed in as `reviewer`.
   - Checks that need repository config (`random_ids` contexts, and `review_required` for "done requires `-s review` first") stay in `Repo.edit`. Keep "nothing to change" before `find` there too, because `tests/test_mcp.py` expects it for a missing task.
   - In `src/chitty/run.py`, extract `claim_edit()` and `fail_review_edit(note)`, and use them for the claim and in `_fail_review`. These are the only fixed-shape edits Chitty makes itself, and the property tests build edits through them, so a bug in `run.py` reaches the tests.
   - Existing tests must pass unchanged.
2. **Property tests with Hypothesis** (a new dev dependency in `pyproject.toml`), in `tests/test_check_edit.py`.
   - Generate tasks: any status, 0 to 6 criteria ticked or not, notes, history, and owners.
   - Generate edits: status changes, notes with and without verdict lines, checks and unchecks.
   - At least these properties:
     - `fail_review_edit` is accepted on any `review` task, and `claim_edit` on any `todo` task, when the reviewer is a fresh actor with no work on the task, as `chitty run`'s own actor always is.
     - With `skip_verdicts=False`, `review → done` on a task with criteria is accepted only with a `Reviewed:` note and a `pass` verdict for every criterion.
     - When a `review` edit results in `doing`, the failed reviews since the last block, counting this one, are fewer than `REVIEW_FAILURE_LIMIT`; otherwise the result is `blocked` with owner `human`.
   - Each property must run in well under a second, so these tests stay in `make check`.

Out of scope:
- Restructuring `chitty run` itself.
- Removing the existing slow tests. A later ticket decides which become smoke tests, using what this one shows.

## Acceptance Criteria

- [x] `check_edit` exists, does no I/O (a test calls it with no repository and no `CHITTY_ACTOR`), `Repo.edit` uses it, and all existing tests pass unchanged.
- [x] The new tests add less than 5 seconds to `make check`.
- [x] `tests/test_check_edit.py` has Hypothesis properties for the three rules above, built through `claim_edit` and `fail_review_edit`, which `run.py` uses. Removing `skip_verdicts=True` from `fail_review_edit` makes the first property fail with a shrunk counterexample, recorded in the summary.

## Plan

Extract pure check_edit validation from Repo.edit, add run.py claim/fail helpers, and cover the specified edit rules with fast Hypothesis properties. Keep config-dependent checks in Repo.edit, run regression tests before and after the fix, then format and run make check.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-221/1`; the reintroduced `TASK-206` bug was caught, and the shrunk counterexample was a `review` task with one unticked criterion and empty history; the six properties take about 0.9 s). Outcomes:
- Config-dependent checks can't be pure: fixed, they stay in `Repo.edit`.
- A hard-coded edit in the test wouldn't see a `run.py` bug: fixed, extract `claim_edit` and `fail_review_edit`.
- The first property failed for reviewers with work on the task: fixed, the reviewer is a fresh actor, as in `chitty run`.
- The escalation property was ambiguous: fixed, this failure counts.
- `skip_verdicts` bypasses the `done` rule: fixed, the property pins it off.
- "Nothing to change" before `find`: fixed.
- Zero-criteria tickets accept any verdict text on `review → done`: noted as a possible follow-up, not filed, because with no criteria there's nothing to judge.
- Size: confirmed right for a pilot.

Implemented and verified. Pure check_edit has no I/O and preserves config-dependent checks in Repo.edit. Extracted claim_edit and fail_review_edit; the property suite uses both. make check passed (353 Python tests and Node tests); Hypothesis properties took 0.27s in isolation. Verified the regression guard: without skip_verdicts, the shrunk one-criterion review case fails on missing verdict 1.

Reviewed: inspected the extraction and property tests; make format && make check passed (354 Python tests and Node tests), focused properties ran in 0.30s, and the missing-verdict regression was reproduced.
1: pass - check_edit is pure and existing tests pass
2: pass - property tests add well under 5 seconds
3: pass - required Hypothesis properties use run.py helpers

## Summary

Implemented pure edit validation in src/chitty/store.py, with run.py helpers claim_edit and fail_review_edit and Hypothesis coverage in tests/test_check_edit.py. Added Hypothesis to dev dependencies and uv.lock. Handoff: review the focused extraction and property generators. Verification: make check passed; explicit no-skip regression produced the expected missing-verdict error.

## History

- 2026-11-06T19:18:51Z youthful-toad → backlog
- 2026-11-06T19:28:21Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T19:28:21Z youthful-toad backlog → todo
- 2026-11-06T20:44:37Z youthful-heron todo → doing
- 2026-11-06T20:44:56Z youthful-heron: wrote the plan
- 2026-11-06T20:49:37Z youthful-heron: changed notes, summary; ticked acceptance criteria
- 2026-11-06T20:49:37Z youthful-heron doing → review
- 2026-11-06T21:06:32Z jolly-puffin: changed notes; ticked acceptance criteria
- 2026-11-06T21:06:32Z jolly-puffin review → done
- 2026-11-11T10:18:02Z vivid-yellowhammer: changed parent
