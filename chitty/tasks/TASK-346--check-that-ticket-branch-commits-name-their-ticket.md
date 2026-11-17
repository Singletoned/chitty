---
title: Check that ticket branch commits name their ticket
status: cold-read
created: 2026-11-16
---

## Description

`src/chitty/roles/work.md` tells workers to end implementation commits with `Task: <ID>`, so `git log --grep <ID>` finds them. Check it at `-s review` instead of relying on the guide.

Decisions:

- Add a pure function `commits_missing_trailer(commits: Sequence[Commit], task_id: TaskId) -> list[Commit]` in `src/chitty/git.py`, with a frozen dataclass `Commit(sha: str, message: str)`. It returns, in input order, every commit whose subject (first line) does not start with `chitty: ` and whose last paragraph (the lines after the last blank line, when the message has more than one paragraph) has no line equal to `Task: <ID>` after stripping whitespace. A one-paragraph message has no trailers.
- Add `git.branch_commits(root: Path, main_branch: str) -> list[Commit]`: the non-merge commits reachable from `HEAD` but not from `main_branch` (`git rev-list --no-merges <main>..HEAD`), oldest first, with full messages.
- In `Repo.edit` in `src/chitty/store.py`, under exactly the condition of the existing uncommitted-changes refusal (entering review from another status, in a git checkout, without `skip_current_version`), and right after it, refuse when `commits_missing_trailer(branch_commits(...), task_id)` is not empty. The `ChittyError` starts `cannot move <ID> to review; these commits lack a Task: <ID> trailer:` and lists each commit as `<short sha> <subject>`, one per line, then says to reword them (for example with `git rebase -i`) and retry. Nothing is written or committed. On `main` itself the list is empty, so nothing changes there.
- Existing tests that commit on a ticket branch and then enter review, including fake agent scripts in runner tests, will start failing: give those commits the trailer. Do not weaken the rule to make them pass.
- In `work.md`, replace ``Commit those in small logical commits ending with `Task: <ID>` using that ticket's ID, so `git log --grep <ID>` finds them.`` with ``Commit those in small logical commits ending with a `Task: <ID>` trailer; `chitty edit -s review` refuses branch commits without one.``

Tests: Hypothesis property tests for `commits_missing_trailer` (as `tests/test_property_next.py` uses Hypothesis), and real-repository tests inheriting `ReviewMergeTestCase` from `tests/test_review_merge.py`, all in a new `tests/test_review_trailers.py`. Add `Commit`, `branch_commits` and `commits_missing_trailer` first, raising `NotImplementedError`, so the tests fail on behaviour rather than import.

Out of scope: checking commits outside review, rewording commits automatically, and other trailers.

## Acceptance Criteria

- [ ] Hypothesis property on `commits_missing_trailer`: generate lists of commits, each with a subject that starts with `chitty: ` or not, a body that is absent or present, and a last paragraph holding `Task: <this ID>`, `Task: <another ID>`, another trailer, or nothing, with optional surrounding whitespace on the trailer line. The result is exactly the commits that are not `chitty: ` commits and lack this ID's trailer, in input order. Fails before the change.
- [ ] Example tests on `commits_missing_trailer`: a single-line message `Task: TASK-1` is missing (one paragraph); `Fix\n\nTask: TASK-1` is not; `Fix\n\nTask: TASK-1\n\nMore text` is missing (the trailer is not in the last paragraph); `Fix\n\nTask: TASK-10` is missing for `TASK-1`.
- [ ] Real repository on branch `task-1` with `TASK-1` in `doing`: after one commit `Add x` without a trailer, `chitty edit 1 -s review` exits 1, its output names that commit's short sha and `Add x`, and `TASK-1` stays `doing`. After rewording it to end with `Task: TASK-1`, the same command moves `TASK-1` to `review`. A merge of `main` into the branch and Chitty's own `chitty: ` autocommits never block. Fails on `main`.
- [ ] A direct `Repo.edit` with `Edit(status="review", skip_current_version=True)` on a branch with a commit lacking the trailer moves the ticket to `review`.
- [ ] The `work.md` sentence is replaced as the Description says, and `tests/test_guide_work_commits.py` still passes, asserting `refuses branch commits without one`. `make check` passes.

## History

- 2026-11-16T09:59:56Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:39Z intrepid-coral-raven backlog → planning
- 2026-11-17T16:35:05Z kind-umber-toad: changed description, acceptance criteria
- 2026-11-17T16:35:05Z kind-umber-toad planning → cold-read
