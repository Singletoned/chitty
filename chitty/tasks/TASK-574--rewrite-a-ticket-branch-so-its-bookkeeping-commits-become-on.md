---
title: Rewrite a ticket branch so its bookkeeping commits become one
status: planning
depends_on:
  - TASK-339
created: 2026-11-22
---

## Description

After `TASK-339` lands (`BranchCommit`, `SquashPlan` and `squash_plan` in `src/chitty/git.py`), add the Git rewrite that applies a plan to a ticket branch. Split from `TASK-339` on 2026-11-22; `TASK-573` then calls it from landing. Definitions of bookkeeping and implementation commits are in `TASK-339`.

Decisions:

- New `squash_bookkeeping(root: Path, main_branch: str, branch: str, task_id: TaskId, ticket_directories: Sequence[PurePosixPath]) -> int` in `src/chitty/git.py`, run in a clean worktree on `branch`. It refuses merge commits as `add_task_trailers` does, builds `BranchCommit`s (paths from `git diff-tree --no-commit-id --name-only -r -z --no-renames <sha>`), and calls `squash_plan`. On `None` it returns `0` and changes nothing. Otherwise, with `old_tip` the current `HEAD`: `git reset --hard <main_branch>`, `git cherry-pick` each `keep` commit (these touch no ticket path, so they apply cleanly), then make the ticket directories match `old_tip` exactly, deletions included (a retitled ticket renames its file), for example `git restore --source=<old_tip> --staged --worktree -- <dirs>`, passing only the ticket directories present in `old_tip` or `main_branch` (`git restore` exits 1 on a pathspec that matches nothing), and make one commit with subject `chitty: land <task_id>`, body `Squashed <n> Chitty bookkeeping commits.`, and the trailer `Task: <task_id>`. It returns the number of squashed commits. The final tree must equal `old_tip`'s tree. Any failure after the reset (a cherry-pick, the restore, the commit, or a tree mismatch) runs `git cherry-pick --abort` if one is in progress, then `git reset --hard <old_tip>`, then raises `ChittyError` naming the step, so the branch is never left rewritten.
- Out of scope: calling it from landing (`TASK-573`).

Tests in a new `tests/test_squash_bookkeeping_git.py`, with Hypothesis (the repository's property tool).

- Real-Git property (`max_examples=20`, `deadline=None`), in a temporary repository with `git init -b main`, an identity, `chitty/tasks/TASK-1--t.md` and `src/a.py` committed on `main`, and a branch `task-1` in a linked worktree: ticket directories `chitty/tasks` and `chitty/human` (the second has no files anywhere, so the restore must skip it); draw a sequence of two to six commits on the branch, each either a bookkeeping commit (rewrite the ticket file with drawn text plus a counter so it always changes, or now and then rename it to `TASK-1--<drawn slug>-<counter>.md`, subject `chitty: edit TASK-1`) or an implementation commit (write a file `src/<drawn name>.py` with content that includes a counter, a subject from `st.text(alphabet=<printable characters without newlines>, min_size=1).map(str.strip).filter(bool)` (Git strips whitespace and rejects empty messages), and an author name drawn from `st.text(alphabet=string.ascii_letters + string.digits, min_size=1)`; Git rewrites or rejects some other names). Assert author names and dates, not committers (cherry-pick sets the committer). Read each commit's subject, author name and date back with `git log` before squashing and compare against those, not the drawn strings. Track the ticket file's current name across renames. The expected outcome is computed from the draws (fewer than two bookkeeping commits means unchanged), not by calling `squash_plan`. After `squash_bookkeeping`: the tree of `HEAD` equals the old tip's; when the plan was not `None`, the branch is the implementation commits in their original order (same subjects, author names and `src/` trees) followed by exactly one commit whose subject is `chitty: land TASK-1` and which changes only `chitty/tasks/`; otherwise `HEAD` is unchanged. One example with an implementation commit that also edits the ticket file leaves `HEAD` unchanged. One example with a failure after the reset (patch `chitty.git._git` with a wrapper that raises `ChittyError` only when its first Git argument is `restore` and otherwise calls the original) ends with `HEAD` at the old tip and a clean worktree.

## Acceptance Criteria

- [ ] The real-Git property passes: the final tree equals the old tip's, and the branch is the implementation commits in order followed by one `chitty: land TASK-1` commit changing only `chitty/tasks/`, or is unchanged when fewer than two bookkeeping commits were drawn
- [ ] The ticket-file example leaves `HEAD` unchanged, and the restore-failure example ends with `HEAD` at the old tip and a clean worktree; `make check` passes

## Notes

Planner, 2026-11-22: split from `TASK-339` after its second cold read, whose findings for this half (the failure-example patch target, subjects Git normalises) are applied. Keep in `planning` until `TASK-339` lands, then compare with what landed and cold-read it.

## History

- 2026-11-22T10:13:55Z friendly-jade-stoat → todo
- 2026-11-22T10:14:10Z friendly-jade-stoat: changed description, acceptance criteria, notes
- 2026-11-22T10:14:10Z friendly-jade-stoat todo → planning
