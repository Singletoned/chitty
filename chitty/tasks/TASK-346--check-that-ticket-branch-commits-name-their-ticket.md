---
title: Check that ticket branch commits name their ticket
status: review
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

## Summary

Implemented commit trailer detection and review-entry enforcement; updated guide and fixtures. Verified with make check, focused trailer tests, and tests.test_guide_work_commits. Regression gate test failed with the gate temporarily disabled. Ready for independent review.

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
