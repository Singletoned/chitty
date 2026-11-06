---
title: Let a repository name its main branch
status: backlog
priority: medium
created: 2026-11-06
---

## Description

Chitty assumes the integration branch is called `main`. Repositories that use `master`, or another branch, can't use `chitty run`, and cross-branch ticket reads find nothing. The hard-coded places:
- `main_files` in `src/chitty/git.py`, which reads tickets from `refs/heads/main`;
- `_preflight` in `src/chitty/run.py`, which requires the main checkout to be on `main`;
- `_prepare_review`'s `git.rebase(worktree, "main")`;
- the worktree's `git worktree add ... main`.

Add a required `main_branch` setting to `chitty.toml` (or `[tool.chitty]`), with no default, so a wrong guess can't hide. `chitty init` writes it for a new repository from the main checkout's current branch. On upgrade it adds it the same way, as it adds other missing settings. Every place above uses it. `grep -n '"main"' src/chitty/*.py` should then find only test-irrelevant text.

Guides and prompts (`src/chitty/guide.md`, `src/chitty/roles/`, `src/chitty/integrations/pi/chitty.ts`) say "`main`". Change them to "the main branch (`main_branch` in `chitty.toml`)". That changes the managed block, so bump `__version__` at patch level.

Out of scope: remotes and `origin/HEAD` detection, and pushing.

## Acceptance Criteria

- [ ] Tests in a repository whose `main_branch = "master"` show `chitty run` creating the worktree from `master`, rebasing a review onto `master`, and `chitty list` reading tickets from `master`. A missing `main_branch` fails loudly, naming the setting.
- [ ] `chitty init` writes `main_branch` from the current branch for a new repository and adds it on upgrade. `grep -n '"main"' src/chitty/*.py` finds no branch-name use, and the guides say "the main branch".

## History

- 2026-11-06T16:24:17Z youthful-toad → backlog
