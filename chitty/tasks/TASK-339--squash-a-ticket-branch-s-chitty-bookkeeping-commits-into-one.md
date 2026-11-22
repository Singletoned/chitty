---
title: Squash a ticket branch's Chitty bookkeeping commits into one
status: cold-read
created: 2026-11-16
---

## Description

In the 14 days to 2026-11-16, 2392 of 2870 commits on `main` were `chitty: ...` autocommits. When a ticket lands, collapse its branch's bookkeeping commits into one, keeping implementation commits as they are. The ticket file records its own History, so nothing is lost. Planned 2026-11-22 and split: this ticket adds the rewrite in `src/chitty/git.py`; `TASK-573` calls it from the landing in `src/chitty/run.py`.

Definitions, for the non-merge commits `main_branch..HEAD` (oldest first, as `git.branch_commits` gives) and a set of ticket directories (each context's directory relative to the repository root):

- A bookkeeping commit has a subject starting `chitty: ` and changes only paths inside the ticket directories (`PurePosixPath.is_relative_to`).
- Every other commit is an implementation commit.

Decisions:

- New pure function `squash_plan(commits: Sequence[BranchCommit], ticket_directories: Sequence[PurePosixPath]) -> SquashPlan | None` in `src/chitty/git.py`, with frozen dataclasses `BranchCommit(sha: str, subject: str, paths: tuple[PurePosixPath, ...])` and `SquashPlan(keep: tuple[str, ...], squashed: tuple[str, ...])` (SHAs, oldest first). It returns `None`, meaning leave the branch as it is, when there are fewer than two bookkeeping commits, or when any implementation commit changes a path inside a ticket directory (reordering would then change what that commit contains), or when any commit changes no path (cherry-picking an empty commit stops). Otherwise `keep` is the implementation commits in order and `squashed` the bookkeeping commits in order.
- New `squash_bookkeeping(root: Path, main_branch: str, branch: str, task_id: TaskId, ticket_directories: Sequence[PurePosixPath]) -> int` in `src/chitty/git.py`, run in a clean worktree on `branch`. It refuses merge commits as `add_task_trailers` does, builds `BranchCommit`s (paths from `git diff-tree --no-commit-id --name-only -r -z --no-renames <sha>`), and calls `squash_plan`. On `None` it returns `0` and changes nothing. Otherwise, with `old_tip` the current `HEAD`: `git reset --hard <main_branch>`, `git cherry-pick` each `keep` commit (these touch no ticket path, so they apply cleanly), then make the ticket directories match `old_tip` exactly, deletions included (a retitled ticket renames its file), for example `git restore --source=<old_tip> --staged --worktree -- <dirs>`, passing only the ticket directories present in `old_tip` or `main_branch` (`git restore` exits 1 on a pathspec that matches nothing), and make one commit with subject `chitty: land <task_id>`, body `Squashed <n> Chitty bookkeeping commits.`, and the trailer `Task: <task_id>`. It returns the number of squashed commits. The final tree must equal `old_tip`'s tree. Any failure after the reset (a cherry-pick, the restore, the commit, or a tree mismatch) runs `git cherry-pick --abort` if one is in progress, then `git reset --hard <old_tip>`, then raises `ChittyError` naming the step, so the branch is never left rewritten.
- Out of scope: commits made on `main` directly (planning edits in the main checkout); calling it from landing (`TASK-573`).

Tests in a new `tests/test_squash_bookkeeping.py`, with Hypothesis (the repository's property tool).

- `squash_plan` property: draw zero to eight commits, each with a subject (drawn text, prefixed `chitty: ` or not) and one to three paths from `chitty/tasks/<name>.md`, `chitty/human/<name>.md`, `chitty/tasksX/<name>.md` and `src/<name>.py`; ticket directories `chitty/tasks` and `chitty/human`. Expected, computed in the test from the drawn values by the definitions above: `None` in the two stated cases, else `keep` and `squashed` partition the SHAs in order. Mutant tests with `hypothesis.find`: a version that uses `str.startswith` on paths, and one that skips the implementation-commit check, each produce a mismatch.
- Real-Git property (`max_examples=20`, `deadline=None`), in a temporary repository with `git init -b main`, an identity, `chitty/tasks/TASK-1--t.md` and `src/a.py` committed on `main`, and a branch `task-1` in a linked worktree: ticket directories `chitty/tasks` and `chitty/human` (the second has no files anywhere, so the restore must skip it); draw a sequence of two to six commits on the branch, each either a bookkeeping commit (rewrite the ticket file with drawn text plus a counter so it always changes, or now and then rename it to `TASK-1--<drawn slug>-<counter>.md`, subject `chitty: edit TASK-1`) or an implementation commit (write a file `src/<drawn name>.py` with content that includes a counter, a drawn subject of printable text without newlines, and an author name drawn from `st.text(alphabet=string.ascii_letters + string.digits, min_size=1)`; Git rewrites or rejects some other names). Assert author names and dates, not committers (cherry-pick sets the committer). After `squash_bookkeeping`: the tree of `HEAD` equals the old tip's; when the plan was not `None`, the branch is the implementation commits in their original order (same subjects, author names and `src/` trees) followed by exactly one commit whose subject is `chitty: land TASK-1` and which changes only `chitty/tasks/`; otherwise `HEAD` is unchanged. One example with an implementation commit that also edits the ticket file leaves `HEAD` unchanged. One example with a failure after the reset (patch `git.restore` or the `_git` call for the restore to raise `ChittyError`) ends with `HEAD` at the old tip and a clean worktree.

## Acceptance Criteria

- [ ] The `squash_plan` property passes, and both mutant tests find a mismatch
- [ ] The real-Git property, the ticket-file example and the failure example pass; `make check` passes

## History

- 2026-11-16T09:50:21Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:29Z intrepid-coral-raven backlog → planning
- 2026-11-22T10:11:12Z friendly-jade-stoat: changed title, description, acceptance criteria
- 2026-11-22T10:11:12Z friendly-jade-stoat planning → cold-read
- 2026-11-22T10:12:38Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T10:12:38Z friendly-jade-stoat cold-read → planning
- 2026-11-22T10:12:40Z friendly-jade-stoat planning → cold-read
