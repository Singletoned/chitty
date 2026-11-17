---
title: Check that ticket branch commits name their ticket
status: done
labels:
  - needs-minor
created: 2026-11-16
---

## Description

`src/chitty/roles/work.md` tells workers to end implementation commits with `Task: <ID>`, so `git log --grep <ID>` finds them. Check it at `-s review` instead of relying on the guide.

Decisions:

- Add a pure function `commits_missing_trailer(commits: Sequence[Commit], task_id: TaskId) -> list[Commit]` in `src/chitty/git.py`, with a frozen dataclass `Commit(sha: str, message: str)`. It returns, in input order, every commit whose subject (first line) does not start with `chitty: ` and whose last paragraph has no line equal to `Task: <ID>` after stripping whitespace. To find the last paragraph, strip trailing whitespace from the whole message, then take the lines after the last blank line, where a whitespace-only line counts as blank. A one-paragraph message has no trailers.
- Add `git.branch_commits(root: Path, main_branch: str) -> list[Commit]`: the non-merge commits reachable from `HEAD` but not from `main_branch` (`git rev-list --no-merges <main>..HEAD`), oldest first, with full messages. `Repo.edit` passes `self.config.main_branch`. If `git` fails (for example no such branch), the `ChittyError` from `_git` propagates.
- In `Repo.edit` in `src/chitty/store.py`, only when entering review (`edit.status == "review"` and the previous status is not `review`), in a git checkout, and without `skip_current_version`, right after the existing uncommitted-changes refusal: refuse when `commits_missing_trailer(branch_commits(...), task_id)` is not empty. Unlike that refusal it does not run on `review` to `done`, because the reviewer may commit on the branch. The `ChittyError` starts `cannot move <ID> to review; these commits lack a Task: <ID> trailer:` and lists each commit as `<git rev-parse --short sha> <subject>`, one per line, then says to reword them (for example with `git rebase -i`) and retry. Nothing is written or committed. On `main` itself the list is empty.
- Existing tests that commit on a ticket branch and then enter review, including fake agent scripts in runner tests (for example the work agent in `ReviewMergeTestCase` in `tests/test_review_merge.py`), will start failing: give those commits a `-m` message whose last paragraph is `Task: <ID>`. Do not weaken the rule to make them pass.
- In `work.md`, replace ``Commit those in small logical commits ending with `Task: <ID>` using that ticket's ID, so `git log --grep <ID>` finds them.`` with ``Commit those in small logical commits ending with a `Task: <ID>` trailer; `chitty edit -s review` refuses branch commits without one.``

`needs-minor`: `chitty edit -s review` now refuses branch commits without the trailer.

Tests: Hypothesis property tests for `commits_missing_trailer` (as `tests/test_property_next.py` uses Hypothesis), and real-repository tests inheriting `ReviewMergeTestCase` from `tests/test_review_merge.py`, all in a new `tests/test_review_trailers.py`. Add `Commit`, `branch_commits` and `commits_missing_trailer` first, raising `NotImplementedError`, so the tests fail on behaviour rather than import.

Out of scope: checking commits outside review, rewording commits automatically, other trailers, and commits whose subject starts `chitty: ` without Chitty making them.

## Acceptance Criteria

- [x] Hypothesis property on `commits_missing_trailer`: generate lists of commits, each with a subject that starts with `chitty: ` or not, and zero or more further paragraphs, each holding `Task: <this ID>`, `Task: <another ID>`, another trailer, or plain text, with optional surrounding whitespace on lines and trailing blank lines. The result is exactly the commits that are not `chitty: ` commits and whose last paragraph lacks this ID's trailer, in input order; a `Task: <this ID>` line in an earlier paragraph does not count. Fails before the change.
- [x] Example tests on `commits_missing_trailer`: a single-line message `Task: TASK-1` is missing (one paragraph); `Fix\n\nTask: TASK-1` is not; `Fix\n\nTask: TASK-1\n\nMore text` is missing (the trailer is not in the last paragraph); `Fix\n\nTask: TASK-10` is missing for `TASK-1`.
- [x] Real repository on branch `task-1` with `TASK-1` in `doing`: after one commit `Add x` without a trailer, `chitty edit 1 -s review` exits 1, its output contains `git rev-parse --short` of that commit and `Add x`, and `TASK-1` stays `doing`. After rewording it to end with `Task: TASK-1`, the same command moves `TASK-1` to `review`. A merge commit from `main` into the branch and Chitty's own `chitty: ` autocommits never block. Fails before the change.
- [x] Guards, which pass before the change too: a direct `Repo.edit` with `Edit(status="review", skip_current_version=True)` on a branch with a commit lacking the trailer moves the ticket to `review`; and a commit without a trailer made while the ticket is in `review` does not stop `review` to `done`.
- [x] The `work.md` sentence is replaced as the Description says, and `tests/test_guide_work_commits.py` still passes, asserting `refuses branch commits without one`. `make check` passes.

## Plan

Implement commit trailer validation as specified: add Commit and pure trailer detection plus branch commit discovery; enforce it only on entry to review after the dirty-tree guard; update focused tests and work guide, then run format/check and commit.

## Notes

The review-entry regression test failed as expected with the trailer gate temporarily disabled, then passed with it enabled. make check and the focused work-guide test passed.

Review failed (tests): Newly discovered coverage gaps must be fixed; no earlier review notes exist.
1: fail - `tests/test_review_trailers.py::test_missing_trailers` generates at most one further paragraph, no surrounding whitespace, and always the same trailing blanks. Generate multiple paragraphs and variable whitespace, including an earlier matching trailer followed by a nonmatching final paragraph. The current test passes; replacing the function with a NotImplementedError stub produces one error.
2: pass - `uv run python -m unittest tests.test_review_trailers` printed OK; the four specified examples are asserted.
3: fail - `test_review_entry_requires_trailer` passes and fails with exit code 0 instead of 1 when the gate is disabled, but no test creates and merges a main branch commit before review. Add that real merge case and assert it and Chitty autocommits do not block.
4: fail - `test_skip_current_version_bypasses_gate` creates no branch commit without a trailer, so it does not exercise the specified bypass. Add such a commit and assert review status. The review-to-done test passes.
5: fail - `make format && make check` passed, and the work guide has the specified sentence, but `tests/test_guide_work_commits.py` does not assert `refuses branch commits without one`; add the assertion.

Addressed review coverage gaps: the Hypothesis property now varies multiple paragraphs, whitespace, and trailing blanks; real-repository coverage includes a main merge and chitty: commit; the skip-version guard commits an untrailed change; guide test asserts the refusal wording. Focused tests and make format && make check pass.

Reviewed: Earlier coverage findings are resolved.
1: pass - Focused Hypothesis property passed; replacing the function with a NotImplementedError stub produced FAILED (errors=1). Multiple paragraphs and whitespace are generated.
2: pass - `uv run python -m unittest tests.test_review_trailers tests.test_guide_work_commits` printed OK for 6 tests, including the four examples.
3: pass - The real repository test passed with the merge and chitty commit; patching the gate to return an empty list produced FAILED with exit code 0 instead of 1.
4: pass - The focused suite printed OK; bypass uses an untrailed commit and review to done runs after another untrailed commit.
5: pass - The guide and assertion contain the required sentence; `make format && make check` printed OK for 600 tests, with format, ruff and pyright passing.

## Summary

Trailer validation implementation and requested review coverage complete. Verified by make format && make check and focused trailer/guide tests. No follow-ups.

## History

- 2026-11-16T09:59:56Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:39Z intrepid-coral-raven backlog → planning
- 2026-11-17T16:35:05Z kind-umber-toad: changed description, acceptance criteria
- 2026-11-17T16:35:05Z kind-umber-toad planning → cold-read
- 2026-11-17T16:37:57Z kind-umber-toad: changed labels, description, acceptance criteria
- 2026-11-17T16:37:57Z kind-umber-toad cold-read → planning
- 2026-11-17T17:06:27Z kind-umber-toad planning → todo
- 2026-11-17T17:37:08Z friendly-lilac-crane todo → doing
- 2026-11-17T17:37:21Z friendly-lilac-crane: wrote the plan
- 2026-11-17T17:44:06Z friendly-lilac-crane: changed notes, summary; ticked acceptance criteria
- 2026-11-17T17:44:06Z friendly-lilac-crane doing → review
- 2026-11-17T17:46:27Z lively-ebony-adder: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-17T17:46:27Z lively-ebony-adder review → doing
- 2026-11-17T17:55:44Z nimble-indigo-gannet: changed notes, summary; ticked acceptance criteria
- 2026-11-17T17:55:44Z nimble-indigo-gannet doing → review
- 2026-11-17T17:57:44Z friendly-white-otter: changed notes; ticked acceptance criteria
- 2026-11-17T17:57:44Z friendly-white-otter review → done
