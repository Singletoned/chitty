---
title: Save and restore uncommitted worktree work under a named ref
status: planning
parent: TASK-370
created: 2026-11-21
---

## Description

Split from `TASK-370` on 2026-11-21. Before rebasing a ticket worktree onto `main`, the runner must set uncommitted work aside and bring it back afterwards. The shared stash list (`refs/stash`) is shared by every worktree, so concurrent runs and people could pick up or drop each other's entries. This ticket adds two Git helpers that keep the saved work under a ref the caller names instead. `TASK-370` wires them into `chitty run`; nothing calls them in this ticket.

Decisions, in `src/chitty/git.py`, using `_git` for commands that must succeed:

- `save_work(root: Path, ref: str, message: str) -> bool`:
  - if `git status --porcelain` (which leaves out ignored files) is empty, return `False` and change nothing;
  - if `ref` already exists (`git rev-parse --verify --quiet <ref>` succeeds), raise `ChittyError(f"{ref} already exists; apply it with git stash apply {ref} and delete it with git update-ref -d {ref}")` and change nothing;
  - otherwise run `git add -A`, then `git stash create <message>`; if its output is empty, raise `ChittyError` naming `root` (never call `update-ref` with an empty commit); then `git update-ref <ref> <commit>`, `git reset --hard` and `git clean -fd` (which keeps ignored files). Return `True`.
  - It never runs `git stash push`, `pop` or `drop`, and never touches `refs/stash`.
- `restore_work(root: Path, ref: str) -> bool`:
  - run `git -c rerere.enabled=false stash apply <ref>` (no `--index`: staged edits come back unstaged, and files that were new come back added; accepted). Disable rerere as `rebase_onto` does.
  - exit 0: `git update-ref -d <ref>`, return `True`.
  - non-zero exit (for example a conflict, `UU`, or `AA` on a path the current `HEAD` added): `git reset --hard`, `git clean -fd`, keep `ref`, return `False`.
  - a `ref` that does not exist raises `ChittyError` naming it, before running `stash apply`.

Tests: new `tests/test_git_saved_work.py`, real Git in temporary directories (`git init -b main`, local `user.name` and `user.email`), Hypothesis (the repository's property tool) with `@settings(max_examples=25, deadline=None)`, as in `tests/test_git.py`.

- Property `test_save_then_restore_round_trips`: draw 1 to 6 files committed on `main`, and a mix of changes: a tracked file edited and left unstaged, a tracked file edited and staged, a tracked file deleted, new untracked files, and ignored files (listed in a committed `.gitignore`), with random printable contents. Before saving, push one unrelated entry with `git stash push` so `git stash list` is not empty; record it. Record every non-ignored file's bytes (or absence) and every ignored file's bytes. After `save_work(root, "refs/chitty/stash/TASK-1", "m")`: it returns `True`, `git status --porcelain` is empty, `ref` exists, ignored files are unchanged. Then, at random, commit a change to a file that none of the changes touch. After `restore_work`: it returns `True`, every recorded file has its recorded bytes or is absent as recorded, ignored files are unchanged, `ref` no longer exists, and `git stash list` is exactly the recorded list.
- Examples, each with its own repository: a clean worktree (only ignored files changed) returns `False` and creates no ref; an existing ref raises the message above and leaves the worktree bytes and the ref's commit unchanged; a conflict (save an edit to line 1 of `a.txt`, commit a different line 1 on `HEAD`, then restore) returns `False`, leaves `git status --porcelain` empty and the ref pointing at the same commit; a missing ref raises `ChittyError` naming it.

Before implementing, add both functions raising `NotImplementedError`, run the tests and confirm each fails; then implement and run `make check`.

## Acceptance Criteria

- [ ] The round-trip property passes, and fails against the `NotImplementedError` stubs
- [ ] The four example tests pass (clean worktree, existing ref, conflict on restore, missing ref), and each fails against the stubs; `make check` passes

## History

- 2026-11-21T23:10:55Z lively-zinc-newt → planning
