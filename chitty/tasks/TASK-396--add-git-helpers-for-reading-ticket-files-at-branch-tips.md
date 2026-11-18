---
title: Add Git helpers for reading ticket files at branch tips
status: cold-read
parent: TASK-376
created: 2026-11-18
---

## Description

`TASK-378` reads each ticket from one ref tip chosen by `ticket_source` (`TASK-377`), instead of every ref's history. It needs a few Git helpers that do not exist yet. Build them on their own, so `TASK-378` is only `Repo` wiring. Context: `docs/plan/ticket-state.md`, "Planning decisions" (on branch `plan/ticket-state` until it lands on `main`).

Decisions, all in `src/chitty/git.py`, each raising `ChittyError` (through `_git`) on any Git failure not named here:

- `branch_tips(root: Path) -> tuple[dict[str, str], dict[str, str]]`: local branch name to commit, and remote-tracking branch name (`origin/task-5`) to commit. Enumerate with `git for-each-ref --format=%(refname)%09%(objectname)%09%(symref) refs/heads refs/remotes`, skip symbolic refs (`origin/HEAD`), and strip the `refs/heads/` or `refs/remotes/` prefix; never use `%(refname:short)`, which can print `heads/origin/task-5`.
- `is_ancestor(root: Path, ancestor: str, descendant: str) -> bool`: `git merge-base --is-ancestor`; exit 0 is `True`, exit 1 is `False`, any other exit raises. Do not build it on `_git`, which raises on exit 1.
- `ref_commit(root: Path, ref: str) -> str | None`: the commit a ref points at, or `None` when the ref does not exist (an unborn branch counts as not existing).
- `files_at(root: Path, ref: str, directories: Sequence[Path]) -> list[tuple[Path, str]]`: every blob below the directories at that ref's tip, with its text, read with `git ls-tree -r --full-tree` and one `_read_blobs` call, as `main_files` does. `main_files` may be rewritten on top of it.
- `changed_since_merge_base(root: Path, base_of: str, other: str, paths: Sequence[Path]) -> bool`: true when `git diff --quiet <merge-base> <base_of> -- <paths>` reports a change, where the merge base is that of `base_of` and `other`; unrelated histories (no merge base) raise. `TASK-378` builds `changed_on_both` from two calls.

Tests: real-Git tests in `tests/test_git.py`, inheriting `RepoTestCase`, with `git init -b main` and a configured user. No property: each helper wraps one Git command over a fixed set of cases, each in the criteria.

## Acceptance Criteria

- [ ] `branch_tips` returns local and remote-tracking tips, skips `origin/HEAD`, and names a local branch `origin/task-5` (alongside a remote `origin/task-5`) correctly in the local map
- [ ] `is_ancestor` returns `True` for an ancestor and for the same commit, `False` for a non-ancestor, and raises for an unknown commit; `ref_commit` returns `None` for a missing ref and an unborn branch
- [ ] `files_at` returns the ticket files at a branch tip that differ from the working tree, including the archive directory; `changed_since_merge_base` is true only when the first ref changed one of the paths since the merge base, and raises for unrelated histories; `make check` passes

## History

- 2026-11-18T17:51:42Z lively-quartz-crane → backlog
- 2026-11-18T17:51:58Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:51:58Z lively-quartz-crane backlog → planning
- 2026-11-18T17:52:46Z lively-quartz-crane planning → cold-read
