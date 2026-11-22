---
title: Rewrite a ticket branch so its bookkeeping commits become one
status: todo
depends_on:
  - TASK-339
created: 2026-11-22
---

## Description

After `TASK-339` lands (`BranchCommit`, `SquashPlan` and `squash_plan` in `src/chitty/git.py`), add the Git rewrite that applies a plan to a ticket branch. Split from `TASK-339` on 2026-11-22; `TASK-573` then calls it from landing. Definitions of bookkeeping and implementation commits are in `TASK-339`.

Decisions:

- New `squash_bookkeeping(root: Path, main_branch: str, branch: str, task_id: TaskId, ticket_directories: Sequence[PurePosixPath]) -> int` in `src/chitty/git.py`, run in a clean worktree on `branch`. It refuses merge commits as `add_task_trailers` does, builds `BranchCommit`s (paths from `git diff-tree --no-commit-id --name-only -r -z --no-renames <sha>`), and calls `squash_plan`. It expects the caller to have rebased `branch` onto `main_branch` (landing does so first): if `main_branch` is not an ancestor of `HEAD` (`git merge-base --is-ancestor`), it raises `ChittyError` whose message names `main_branch` and says to rebase onto it, and changes nothing. This check comes first, before building the plan. On `None` it returns `0` and changes nothing. Otherwise, with `old_tip` the current `HEAD`: `git reset --hard <main_branch>`, `git cherry-pick` each `keep` commit (these touch no ticket path, so they apply cleanly), then make the ticket directories match `old_tip` exactly, deletions included (a retitled ticket renames its file), for example `git restore --source=<old_tip> --staged --worktree -- <dirs>`, passing only the ticket directories present in `old_tip` or `main_branch` (a directory is present in a revision when `git ls-tree -d --name-only <rev> -- <dir>` prints it) (`git restore` exits 1 on a pathspec that matches nothing), and make one commit with subject `chitty: land <task_id>`, body `Squashed <n> Chitty bookkeeping commits.`, and the trailer `Task: <task_id>`. It returns the number of squashed commits. The final tree must equal `old_tip`'s tree. Any failure after the reset (a cherry-pick, the restore, the commit, or a tree mismatch) runs `git cherry-pick --abort` if `CHERRY_PICK_HEAD` exists (`_git_path(root, "CHERRY_PICK_HEAD")` in `src/chitty/git.py`), then `git reset --hard <old_tip>`, then raises `ChittyError` naming the step, so the branch is never left rewritten.
- Out of scope: calling it from landing (`TASK-573`).

Tests in a new `tests/test_squash_bookkeeping_git.py`, with Hypothesis (the repository's property tool).

- Real-Git property (`max_examples=20`, `deadline=None`), in a temporary repository with `git init -b main`, an identity, `chitty/tasks/TASK-1--t.md` and `src/a.py` committed on `main`, and a branch `task-1` in a linked worktree: ticket directories `chitty/tasks` and `chitty/human` (the second has no files anywhere, so the restore must skip it); draw a sequence of two to six commits on the branch, each either a bookkeeping commit (rewrite the ticket file with drawn text plus a counter so it always changes, or, when a drawn `st.booleans()` is true, rename it to `TASK-1--<drawn slug>-<counter>.md` (slug from the same alphabet, `min_size=1`), subject `chitty: edit TASK-1`) or an implementation commit (write a file `src/<drawn name>.py` (name from `st.text(alphabet=string.ascii_lowercase + string.digits, min_size=1)`) with content that includes a counter, a subject from `st.text(alphabet=<printable characters without newlines>, min_size=1).map(str.strip).filter(bool)` (Git strips whitespace and rejects empty messages), and an author name drawn from `st.text(alphabet=string.ascii_letters + string.digits, min_size=1)`; Git rewrites or rejects some other names). Give each commit a distinct fixed author date through `GIT_AUTHOR_DATE` (for example `2026-01-01T00:00:<counter>+0000`; at most six commits, so the counter stays under 60), and assert author names and author dates (`%an`, `%aI`), not committers (cherry-pick sets the committer). Read each commit's subject, author name and date back with `git log` before squashing and compare against those, not the drawn strings. Track the ticket file's current name across renames. The expected outcome is computed from the draws (fewer than two bookkeeping commits means unchanged), not by calling `squash_plan`. After `squash_bookkeeping`: the tree of `HEAD` equals the old tip's; when the plan was not `None`, the branch is the implementation commits in their original order (same subjects, author names and `src/` trees) followed by exactly one commit whose subject is `chitty: land TASK-1`, whose body is `Squashed <n> Chitty bookkeeping commits.` with `n` the number of bookkeeping commits drawn, whose last paragraph contains `Task: TASK-1`, and which changes only `chitty/tasks/`, and the return value is `n`; otherwise `HEAD` is unchanged and the return value is 0. One example where `main` gained a commit touching `src/b.py` after the branch point raises `ChittyError` whose message contains `main` and `rebase`, and leaves `HEAD` unchanged. One example with an implementation commit that also edits the ticket file leaves `HEAD` unchanged and returns 0. One example with a failure after the reset, on a branch with two bookkeeping commits and one implementation commit so the plan is not `None` (run every Git command in `squash_bookkeeping`, `restore` included, through `_git`; patch `chitty.git._git` with a wrapper that raises `ChittyError` only when its first Git argument is `restore` and otherwise calls the original) asserts the wrapper saw a `restore` call, that `squash_bookkeeping` raised `ChittyError` naming the restore step, and that it ends with `HEAD` at the old tip and a clean worktree.

## Acceptance Criteria

- [ ] The real-Git property passes: the final tree equals the old tip's, and the branch is the implementation commits in order (subjects, author names, author dates, `src/` trees) followed by one `chitty: land TASK-1` commit with the stated body and `Task: TASK-1` trailer, changing only `chitty/tasks/`, with the return value equal to the bookkeeping count; or is unchanged with return value 0 when fewer than two bookkeeping commits were drawn
- [ ] The ticket-file example leaves `HEAD` unchanged and returns 0; the not-rebased example raises `ChittyError` and leaves `HEAD` unchanged; the restore-failure example sees a `restore` call, raises `ChittyError` naming the step, and ends with `HEAD` at the old tip and a clean worktree; `make check` passes

## Notes

Planner, 2026-11-22: split from `TASK-339`, which has landed; this text was compared with what landed (`BranchCommit`, `SquashPlan`, `squash_plan` in `src/chitty/git.py`) and cold-read again.

Planner, 2026-11-22: third cold read checked. Its claim that `git restore --source=<old_tip> --staged --worktree -- chitty/tasks` leaves a renamed-away file behind is wrong: with Git 2.56.0, after `git reset --hard main`, that command staged `R chitty/tasks/TASK-1.md -> chitty/tasks/TASK-1--x.md` and removed the old name (restore runs in no-overlay mode). Its other points are applied.

## History

- 2026-11-22T10:13:55Z friendly-jade-stoat → todo
- 2026-11-22T10:14:10Z friendly-jade-stoat: changed description, acceptance criteria, notes
- 2026-11-22T10:14:10Z friendly-jade-stoat todo → planning
- 2026-11-22T21:26:37Z plucky-umber-wren planning → cold-read
- 2026-11-22T21:29:45Z plucky-umber-wren: changed description
- 2026-11-22T21:29:58Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T21:30:59Z plucky-umber-wren: replaced notes; changed description, acceptance criteria
- 2026-11-22T21:31:59Z plucky-umber-wren: changed description, notes
- 2026-11-22T21:31:59Z plucky-umber-wren cold-read → todo
