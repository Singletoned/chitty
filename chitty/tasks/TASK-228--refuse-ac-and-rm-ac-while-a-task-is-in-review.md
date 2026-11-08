---
title: Refuse `--ac` and `--rm-ac` while a task is in review
status: review
created: 2026-11-07
---

## Description

In `src/chitty/store.py:check_edit`, reject `--ac` and `--rm-ac` while the task is already in `review`, just as `--set-ac` is rejected. Check the pre-edit status, so an edit that also moves `review` to `doing` or `done` cannot change criteria; `doing` to `review` may still change them. Reject before review-note and verdict checks. Leave `--check` and `--uncheck` unchanged. Add regression tests via the CLI and the shared store path with real files in temp repositories. Scope: criterion mutations only.

## Acceptance Criteria

- [x] Fail-first tests show `--ac` and `--rm-ac` each being accepted on a review ticket before the fix, including a combined `review` to `done` edit with a valid verdict. After the fix, each is rejected with a clear message and leaves the file unchanged; `--set-ac` remains rejected.
- [x] Tests show criteria may still change when moving `doing` to `review`, and CLI and shared store validation agree; `make check` passes.

## Plan

Extend check_edit to reject --ac and --rm-ac alongside --set-ac whenever the pre-edit status is review. Add CLI and Repo.edit regression tests, including review-to-done with valid verdict and doing-to-review allowance; verify rejection preserves files. Run focused fail-first tests, then make check and format.

## Notes

Cold-read finding resolved: the refusal is the decision, not an open question; guard pre-edit review status even during a simultaneous status change. Include fail-first CLI and shared-store coverage.

Implementing cold read against the updated ticket: `tests.test_cli.TestEdit.test_edit_rejects_adding_and_removing_criteria_in_review` first failed because `--ac` succeeded; `tests.test_store.TestStore.test_review_criteria_are_immutable_through_repo_edit` first failed because `Repo.edit` accepted it. After the fix all focused tests and `make check` passed (380 Python tests, Node tests). Kept candidate implementation at `refs/cold-read/TASK-228/1`; inspect with `git diff main...refs/cold-read/TASK-228/1` and verify against the criteria before reuse. No remaining serious finding.

Fail-first CLI and Repo.edit tests both failed before the guard: --ac and direct store mutation were accepted. Guard now rejects --ac, --rm-ac, and --set-ac based on pre-edit review status; tests cover review-to-done valid verdict preservation and doing-to-review. make format and make check passed (380 Python tests and Node tests).

Review failed (work): the worktree has uncommitted changes: `src/chitty/store.py`, `tests/test_cli.py`, `tests/test_store.py`.

Reverified both criteria: focused CLI and Repo.edit regressions pass; make format and make check pass (380 Python tests and Node tests). chitty fix completed with existing Markdown warnings in other task files.

## Summary

Rejects --ac, --rm-ac, and --set-ac for tasks already in review, using pre-edit status. CLI and Repo.edit tests cover refusal, unchanged files, valid review-to-done verdict, and allowed doing-to-review edits. Verified focused regressions and make format && make check (380 Python tests and Node tests). No follow-up.

## History

- 2026-11-07T10:09:05Z vivid-dormouse → backlog
- 2026-11-08T14:15:12Z eager-puffin: changed description, acceptance criteria, notes
- 2026-11-08T14:17:49Z eager-puffin: changed notes
- 2026-11-08T14:17:50Z eager-puffin backlog → todo
- 2026-11-08T17:04:21Z plucky-urchin todo → doing
- 2026-11-08T17:04:42Z plucky-urchin: wrote the plan
- 2026-11-08T17:05:51Z plucky-urchin: changed notes; ticked acceptance criteria
- 2026-11-08T17:05:57Z plucky-urchin: changed summary
- 2026-11-08T17:05:57Z plucky-urchin doing → review
- 2026-11-08T17:16:12Z eager-falcon: changed notes
- 2026-11-08T17:16:12Z eager-falcon review → doing
- 2026-11-08T17:47:05Z youthful-zander: changed notes, summary; ticked acceptance criteria
- 2026-11-08T17:47:05Z youthful-zander doing → review
