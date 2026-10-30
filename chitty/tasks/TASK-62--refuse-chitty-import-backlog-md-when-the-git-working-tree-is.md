---
title: Refuse `chitty import backlog-md` when the Git working tree is dirty
status: doing
created: 2026-10-30
---

## Description

The import rewrites many files (tasks, `AGENTS.md`, removed sources). Running it on a dirty tree mixes its changes with unrelated work and leaves no clean point to return to. Refuse unless `git status --porcelain` is empty, including untracked files.

## Acceptance Criteria

- [ ] `chitty import backlog-md` fails before writing anything when tracked files are modified or untracked files exist, naming them
- [ ] It fails loudly outside a Git repository
- [ ] `--remove-source` is removed, since a clean tree means every source is tracked and unmodified
- [ ] `PLAN.md` and `README.md` describe the new rule

## Plan

Add `git.require_clean(root)` that runs `git status --porcelain` and raises `ChittyError` listing entries; call it at the start of `import_directory` (outside a repo the git call itself fails loudly). Drop `source_problems`, `--remove-source` and the `force` path in `remove_sources`. Tests: turn the import test repo into a committed Git repo, add dirty/untracked/no-repo refusal tests.

## History

- 2026-10-30 → todo
- 2026-10-30 todo → doing
