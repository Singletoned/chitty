---
title: Do not leave a failed chitty edit written but uncommitted
status: review
created: 2026-11-16
---

## Description

Seen 2026-11-16 in `.worktrees/task-318`: `chitty edit TASK-318 --depends-on TASK-325 --depends-on TASK-326 --note ...` printed `depends_on TASK-326: no such task` and exited non-zero, but had already written the dependencies, note and history entry to the ticket file, leaving it modified and uncommitted.

Cause: `Repo.edit` in `src/chitty/store.py` writes the file (`_save`, `_write`; `_save` may also `git.move` the file when the title changes), then `_commit` runs `fix` from `src/chitty/check.py` and raises `cannot finalize task write with unresolved problems` without undoing the write. Any problem the post-write check finds but the pre-write checks miss leaves the file behind: a self-dependency, a dependency cycle, a parent cycle, and (until `TASK-356`) a dependency that exists only on another branch.

Make a refused `edit` leave the repository as it was, files and index. Before the write, keep the bytes of every task file in the configured context directories (`fix` inside `_commit` may also rename or rewrite task files, so `change.paths` is not enough). When `_commit` refuses: if `_save` renamed the file, move it back with `git.move(root, new, old)`; then restore every kept file whose bytes differ; then raise the same error. The existing `_file_state` and `_restore_file` helpers in `store.py` restore bytes but not the index. The error text does not change. `add` is out of scope: a new ticket cannot form a cycle, and its only post-write refusal is the cross-branch dependency that `TASK-356` removes. Other writes that call `_commit` (archive, restore, move, delete) are also out of scope.

Files: `src/chitty/store.py`; tests in a new `tests/test_property_refused_write.py`. Tests inherit `RepoTestCase` from `tests/support.py`, whose config has `autocommit = false` and no git repository: in `setUp`, rewrite `chitty.toml` with `autocommit = true`, run `git init` with a user name and email, add `TASK-1` and `TASK-2` (depending on `TASK-1`) through `Repo`, and commit. Build the `Repo` in process as `tests/test_property_inbox.py` does. All Hypothesis examples share that repository; each refused example must leave it as `setUp` did, which is what the property checks.

## Acceptance Criteria

- [x] Hypothesis property in `tests/test_property_refused_write.py`: draw an edit of `TASK-1` that the post-write check refuses (one of: depends on itself, depends on `TASK-2` making a cycle, parent itself), combined with an optional generated note and an optional generated new title. Notes are non-blank, LF only, with no line starting with `#` or a code fence; titles are one line with at least one letter or digit. `Repo.edit` raises `ChittyError` containing `cannot finalize task write`; afterwards `git status --porcelain` is empty and every file under `chitty/` has the same bytes as before. `max_examples` at least 25, `deadline=None`. Fails before the change. `make check` passes.

## Plan

Update the refusal property fixture so chitty.toml is committed into the clean Git baseline, and assert the fixture starts clean and remains clean after every refused edit. Run the focused test, make format and make check, then commit the regression-test correction with a Task: TASK-355 trailer.

## Notes

The regression property failed without rollback: Hypothesis observed both a refused edit leaving changed ticket bytes and a generated case no longer refused after the shared repo had been mutated. With rollback, the property passes for 30 examples and the full suite passes.

Review failed (tests): The property must establish and assert a clean Git status, not merely compare against its baseline.
1: fail - Newly discovered: running TestRefusedEditProperty.setUp and printing repr(case._snapshot()[1]) produced '?? chitty.toml\n'; the property compares statuses without asserting empty, so it does not meet the clean-status requirement. Commit or otherwise track the fixture config and explicitly assert empty status after each edit. make format && make check passed (603 tests); the property passed on this branch and failed against main store.py with a changed-file assertion and Hypothesis FlakyFailure.

Fixed the review finding: the property fixture now commits chitty.toml, asserts the baseline Git status is clean, and verifies status remains clean after every refused edit. Focused property passed; make format and make check passed (603 tests; make check exit 0).

## Summary

Updated the refused-edit property to assert a genuinely clean Git working tree and unchanged chitty/ bytes. Verified with the focused property and make format && make check (603 tests, exit 0). No follow-up known.

## History

- 2026-11-16T10:29:24Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:55Z intrepid-coral-raven backlog → planning
- 2026-11-16T16:56:28Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T16:56:39Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T16:56:42Z open-russet-eel: changed acceptance criteria
- 2026-11-16T16:57:31Z open-russet-eel: changed owner
- 2026-11-16T16:57:31Z open-russet-eel planning → cold-read
- 2026-11-16T17:03:01Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T17:03:01Z open-russet-eel cold-read → planning
- 2026-11-16T17:03:03Z open-russet-eel: changed owner
- 2026-11-16T17:03:03Z open-russet-eel planning → todo
- 2026-11-17T18:01:08Z daring-teal-crane todo → doing
- 2026-11-17T18:02:02Z daring-teal-crane: wrote the plan
- 2026-11-17T18:06:40Z daring-teal-crane: changed notes, summary; ticked acceptance criteria
- 2026-11-17T18:06:40Z daring-teal-crane doing → review
- 2026-11-17T18:09:24Z youthful-khaki-adder: changed acceptance criteria, notes
- 2026-11-17T18:09:24Z youthful-khaki-adder review → doing
- 2026-11-17T18:17:22Z eager-indigo-crane: wrote the plan
- 2026-11-17T18:19:17Z eager-indigo-crane: changed notes, summary; ticked acceptance criteria
- 2026-11-17T18:19:17Z eager-indigo-crane doing → review
