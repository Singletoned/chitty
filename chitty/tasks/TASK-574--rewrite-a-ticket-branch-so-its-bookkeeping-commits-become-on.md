---
title: Rewrite a ticket branch so its bookkeeping commits become one
status: doing
depends_on:
  - TASK-339
created: 2026-11-22
---

## Description

`TASK-339` added `BranchCommit`, `SquashPlan` and `squash_plan` in `src/chitty/git.py`, which decide which commits on a ticket branch are bookkeeping. Add the Git rewrite that applies a plan. `TASK-573` will call it when landing.

New `squash_bookkeeping(root: Path, main_branch: str, branch: str, task_id: TaskId, ticket_directories: Sequence[PurePosixPath]) -> int` in `src/chitty/git.py`, run in a clean worktree on `branch`, with every Git command through `_git`:

1. If `main_branch` is not an ancestor of `HEAD`, raise `ChittyError` naming `main_branch` and saying to rebase onto it; change nothing. Refuse merge commits as `add_task_trailers` does.
2. Build `BranchCommit`s (paths from `git diff-tree --no-commit-id --name-only -r -z --no-renames <sha>`) and call `squash_plan`. On `None`, return 0 and change nothing.
3. With `old_tip` = `HEAD`: `git reset --hard <main_branch>`, cherry-pick each `keep` commit, then `git restore --source=<old_tip> --staged --worktree --` the ticket directories that exist in `old_tip` or `main_branch` (restore fails on a pathspec that matches nothing; it also removes a renamed-away ticket file). Commit with subject `chitty: land <task_id>`, body `Squashed <n> Chitty bookkeeping commits.` and trailer `Task: <task_id>`. Check the new tree equals `old_tip`'s; return `n`.
4. Any failure in step 3: `git cherry-pick --abort` if `CHERRY_PICK_HEAD` exists (`_git_path`), `git reset --hard <old_tip>`, then raise `ChittyError` naming the step. The branch is never left rewritten.

Tests in a new `tests/test_squash_bookkeeping_git.py`, Hypothesis (`max_examples=20`, `deadline=None`), real Git in a temporary repository: `main` has `chitty/tasks/TASK-1--t.md` and `src/a.py`; branch `task-1` in a linked worktree; ticket directories `chitty/tasks` and `chitty/human` (the second never has files).

- Property: draw two to six commits, each either bookkeeping (subject `chitty: edit TASK-1`; rewrite the ticket file, or rename it to `TASK-1--<slug>.md`) or implementation (a new or changed `src/<name>.py`, any one-line subject, any author name). Alphabets: ticket text `string.ascii_letters + string.digits + " "`; slugs and file names `string.ascii_lowercase + string.digits`, 1 to 20 characters; subjects printable ASCII without newlines, stripped, non-empty; author names `string.ascii_letters + string.digits`, non-empty. Add a counter to every file and name so each commit changes something and names never clash, and give each commit a distinct `GIT_AUTHOR_DATE`. Work out the expected result from the draws, not by calling `squash_plan`, and compare author fields (`%an`, `%aI`), not committers.
- Examples: `main` gained a commit on `src/b.py` after the branch point: `ChittyError` containing `main` and `rebase`, `HEAD` unchanged. An implementation commit that also edits the ticket file: returns 0, `HEAD` unchanged. Two bookkeeping commits and one implementation commit, with `chitty.git._git` patched to raise `ChittyError` on `restore` only: the error names the restore step, and `HEAD` is the old tip with a clean worktree.

Out of scope: calling it from landing (`TASK-573`).

## Acceptance Criteria

- [ ] The real-Git property passes: `HEAD`'s tree equals the old tip's; with two or more bookkeeping commits the branch is the implementation commits in order (subject, author name, author date, `src/` tree) then one `chitty: land TASK-1` commit with the stated body and trailer, changing only `chitty/tasks/`, returning the bookkeeping count; otherwise `HEAD` is unchanged and it returns 0
- [ ] The not-rebased, mixed-commit and restore-failure examples pass as stated; `make check` passes

## Plan

Build and validate the branch plan before rewriting; cherry-pick implementation commits, restore ticket directories, commit and verify the tree, rolling back on failure. Cover generated real Git histories and failure examples, then run checks.

## Summary

Implemented bookkeeping branch rewrite with tree verification and rollback, plus real Git property and failure tests. make check passed.

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
- 2026-11-22T21:32:24Z tidy-zinc-stoat todo → doing
- 2026-11-22T21:34:27Z tidy-zinc-stoat: wrote the plan
- 2026-11-22T21:34:59Z tidy-zinc-stoat: changed owner, notes
- 2026-11-22T21:34:59Z tidy-zinc-stoat doing → planning
- 2026-11-26T20:07:39Z zesty-ginger-newt: changed notes
- 2026-11-26T20:07:39Z zesty-ginger-newt planning → to-plan
- 2026-11-26T20:07:42Z zesty-ginger-newt: replaced notes; changed description, acceptance criteria; wrote the plan
- 2026-11-26T20:07:42Z zesty-ginger-newt to-plan → planning
- 2026-11-26T20:07:44Z zesty-ginger-newt planning → todo
- 2026-11-27T00:09:34Z able-white-gannet todo → doing
- 2026-11-27T00:13:02Z able-white-gannet: wrote the plan
- 2026-11-27T00:20:06Z able-white-gannet: changed summary
