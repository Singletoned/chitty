---
title: Restore saved worktree work from a `refs/chitty/stash` ref
status: cold-read
depends_on:
  - TASK-524
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-524` on 2026-11-21. `TASK-524` adds `git.save_work(root, ref, message)` and `_check_saved_work_ref(ref)` in `src/chitty/git.py`, which save uncommitted work under a ref in `refs/chitty/stash/`. This ticket adds the matching `restore_work`. `TASK-524` landed both names on `main` (rechecked 2026-11-22); its tests are `SavedWorkTests` in `tests/test_git_saved_work.py` (a `unittest.TestCase` with a `git` helper and a `setUp` that makes a repository with committed `a.txt`): add the restore tests to that class.

- `restore_work(root: Path, ref: str) -> bool`, in `src/chitty/git.py`.
- Call `_check_saved_work_ref(ref)` first. A `ref` that does not exist raises `ChittyError` naming it, before running `stash apply`.
- Run `git -c rerere.enabled=false stash apply <ref>` (no `--index`: staged edits come back unstaged, and files that were new come back added; accepted). Disable rerere as `rebase_onto` does.
- Exit 0: `git update-ref -d <ref>`, return `True`.
- Non-zero exit (a conflict `UU`, or `AA` on a path the current `HEAD` added): `git reset --hard`, `git clean -fd`, keep `ref`, return `False`.
- Accepted: if `HEAD` has since made a saved new file's path ignored and an ignored file now sits there, `stash apply` overwrites it; no check.

Tests in `tests/test_git_saved_work.py`, each in its own repository, saving with `save_work` first: a plain round trip (edit `a.txt`, add untracked `u.txt`, save, restore) returns `True`, restores both files' bytes and deletes the ref; a conflict (save an edit to line 1 of `a.txt`, commit a different line 1 on `HEAD`, restore) returns `False`, leaves `git status --porcelain` empty and the ref at the same commit; an `AA` collision (save a new `n.txt`, commit a different `n.txt` on `HEAD`, restore) returns `False` with the worktree matching `HEAD` and the ref kept; a missing ref raises `ChittyError` naming it; `refs/stash` raises the namespace message.

## Acceptance Criteria

- [ ] The five restore tests pass and fail against a `NotImplementedError` stub; `make check` passes

## History

- 2026-11-22T00:06:29Z lively-zinc-newt → planning
- 2026-11-22T00:27:06Z lively-zinc-newt: changed description
- 2026-11-22T00:27:06Z lively-zinc-newt planning → cold-read
