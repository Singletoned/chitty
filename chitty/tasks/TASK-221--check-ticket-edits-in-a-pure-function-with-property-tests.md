---
title: Check ticket edits in a pure function, with property tests
status: backlog
labels:
  - spec-first
priority: medium
parent: TASK-106
created: 2026-11-06
---

## Description

`chitty run` is tested almost only through real Git repositories, worktrees and fake-agent processes, about 150 of `make check`'s 290 seconds. Even so, on 2026-11-06 those tests missed bugs that came from ticket states their fixtures never built. One of them: `_fail_review` moving a ticket with criteria `review → doing` was refused for missing verdict lines (`TASK-206`).

The human wants to move towards pure decision functions tested with property-based tests, and to run the real-Git runs only as a few smoke tests before landing. This ticket is the first, small slice, and a candidate for the spec-first pilot (`TASK-109`).

1. **A pure function.** Move the checks in `Repo.edit` (`src/chitty/store.py`, from "nothing to change" through `_validate_review_verdict`, the independence check and `_escalate_repeated_failure`) into a pure `check_edit(task, edit, reviewer) -> Edit`. It returns the edit to apply, after escalation, or raises `ChittyError` with today's messages.
   - It reads no files, no Git and no environment. `Repo.edit` calls it with `actor()` passed in as `reviewer`.
   - Existing tests must pass unchanged.
2. **Property tests with Hypothesis** (a new dev dependency in `pyproject.toml`), in `tests/test_check_edit.py`.
   - Generate tasks: any status, 0 to 6 criteria ticked or not, notes, history, and owners.
   - Generate edits: status changes, notes with and without verdict lines, checks and unchecks.
   - At least these properties:
     - Every edit that Chitty itself makes is accepted for every task it applies to: `_fail_review`'s edit on any `review` task, and the claim `todo → doing` on any `todo` task.
     - `review → done` is accepted only with a `Reviewed:` note and a `pass` verdict for every criterion.
     - The result never has more failed reviews since the last block than `REVIEW_FAILURE_LIMIT` allows without being `blocked`.
   - Each property must run in well under a second, so these tests stay in `make check`.

Out of scope:
- Restructuring `chitty run` itself.
- Removing the existing slow tests. A later ticket decides which become smoke tests, using what this one shows.

## Acceptance Criteria

- [ ] `check_edit` exists, does no I/O (a test calls it with no repository and no `CHITTY_ACTOR`), `Repo.edit` uses it, and all existing tests pass unchanged.
- [ ] `tests/test_check_edit.py` has Hypothesis properties for the three rules above. Re-adding `TASK-206`'s bug (removing `skip_verdicts` from `_fail_review`'s edit) makes the first property fail with a shrunk counterexample, recorded in the summary.
- [ ] The new tests add less than 5 seconds to `make check`.

## History

- 2026-11-06T19:18:51Z youthful-toad → backlog
