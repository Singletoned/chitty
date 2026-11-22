---
title: Restore saved worktree work from a `refs/chitty/stash` ref
status: doing
depends_on:
  - TASK-524
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-524` on 2026-11-21. `TASK-524` adds `git.save_work(root, ref, message)` and `_check_saved_work_ref(ref)` in `src/chitty/git.py`, which save uncommitted work under a ref in `refs/chitty/stash/`. This ticket adds the matching `restore_work`. `TASK-524` landed both names on `main` (rechecked 2026-11-22); its tests are `SavedWorkTests` in `tests/test_git_saved_work.py` (a `unittest.TestCase` with a `git` helper and a `setUp` that makes a repository with committed `a.txt`): add the restore tests to that class.

- `restore_work(root: Path, ref: str) -> bool`, in `src/chitty/git.py`.
- Call `_check_saved_work_ref(ref)` first. Then, if `git rev-parse --verify --quiet <ref>` fails, raise `ChittyError(f"{ref} does not exist")`. Then, if `git status --porcelain --untracked-files=all` is not empty, raise `ChittyError(f"cannot restore {ref}: the worktree has uncommitted changes")` and change nothing (decided 2026-11-22: a cold reader showed the cleanup below would otherwise delete unrelated untracked files; the runner restores straight after a clean rebase, so the worktree is clean there).
- Run `git -c rerere.enabled=false stash apply <ref>` (no `--index`: staged edits come back unstaged, and files that were new come back added; accepted). Disable rerere as `rebase_onto` does.
- Exit 0: `git update-ref -d <ref>`, return `True`.
- Non-zero exit (a conflict `UU`, or `AA` on a path the current `HEAD` added): `git reset --hard`, `git clean -fd`, keep `ref`, return `False`.
- Accepted: if `HEAD` has since made a saved new file's path ignored and an ignored file now sits there, `stash apply` overwrites it; no check.

Tests in `tests/test_git_saved_work.py`, each in its own repository (`setUp` commits `a.txt` holding `original`), saving with `save_work` first: a plain round trip (edit `a.txt`, add untracked `u.txt`, save, restore) returns `True`, restores both files' bytes and deletes the ref; a conflict (write `saved\n` to `a.txt`, save, write `head\n` to `a.txt` and commit it, restore) returns `False`, leaves `git status --porcelain` empty and the ref at the same commit; an `AA` collision (create `n.txt` holding `saved`, save, create `n.txt` holding `head`, `git add n.txt` and commit, restore) returns `False` with the worktree matching `HEAD` and the ref kept; a missing ref raises `refs/chitty/stash/TASK-1 does not exist`; a dirty worktree (save an edit, then create an untracked `precious.txt`, restore) raises the uncommitted-changes message, keeps `precious.txt` and the ref; `refs/stash` raises the namespace message.

## Acceptance Criteria

- [ ] The six restore tests pass (round trip, conflict, `AA`, missing ref, dirty worktree, `refs/stash`) and fail against a `NotImplementedError` stub; `make check` passes

## History

- 2026-11-22T00:06:29Z lively-zinc-newt → planning
- 2026-11-22T00:27:06Z lively-zinc-newt: changed description
- 2026-11-22T00:27:06Z lively-zinc-newt planning → cold-read
- 2026-11-22T00:28:36Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T00:28:36Z lively-zinc-newt cold-read → todo
- 2026-11-22T01:11:29Z nimble-pearl-adder todo → doing
