---
title: Add a `BACKLOG` context with random IDs
status: backlog
priority: high
depends_on:
  - TASK-177
parent: TASK-106
created: 2026-11-05
---

## Description

First of three parts. The human decided on 2026-11-05 that tickets raised by workers and reviewers should go to backlog with a separate, non-sequential ID, and be assessed in the planning session, which turns them into normally numbered tickets later. Then only `main` hands out sequential numbers. This supersedes `TASK-61`, which reached the same place through the inbox.

This part adds the context and its IDs. Add `random_ids: bool` to `ContextConfig` in `src/chitty/config.py`, named for its effect. A context with it gets random numbers from 10000000 to 99999999, such as `BACKLOG-48213907`: `ID_RE` needs a first digit of 1 to 9, and `TaskId` holds an integer, so this needs no change to it, its ordering, filenames or `ID_RE`. In `Repo.next_number` call a module-level `_random_number()` using `secrets.randbelow`, which a test can patch, retrying a bounded number of times if a known ticket uses the number, and raising a `ChittyError` if none is free. Known tickets include other branches', through `TASK-177`.

Add a `backlog` context with prefix `BACKLOG` and `random_ids = true` to `INITIAL_CONFIG`. `chitty init` must add it to existing repositories: `_add_missing_settings` in `src/chitty/store.py` only adds top-level keys, so write a function like `_add_missing_human_review`. In `pyproject.toml` insert after the last `[tool.chitty.contexts.*]` table, not at the end of the file. Skip it when a `backlog` context or `BACKLOG` prefix already exists, or `RepoConfig._consistent` rejects the result. `ContextConfig` forbids extra keys, so an older Chitty refuses a file with this setting. That is accepted: `chitty_version` already says it needs upgrading.

The name collides with nothing: `chitty/backlog/` is a new directory, and the status `backlog` is a separate namespace. `chitty next` skips the status, and `list` and sorting cope with 8-digit numbers.

Out of scope: when a ticket uses this context, which is the next two parts; IDs made of words, as in `BACKLOG-ember-dolphin-1`, because `TaskId.number` is an integer used throughout; and any change to `TASK-` numbering.

## Acceptance Criteria

- [ ] A test with a linked worktree shows plain `chitty add` creating a `BACKLOG-<8 digits>` ticket in `backlog`, whatever `-s` says, and `-c human` still numbering normally, and fails on a repeated random number by retrying
- [ ] A test shows `edit -s todo` refused on such a ticket, and `chitty move <ID> tasks` on `main` giving it the next `TASK-` number, keeping `backlog`, with references rewritten
- [ ] A test shows `chitty init` adding the context to an existing repository, `chitty check` passing with these tickets present, and `chitty next` never selecting one
- [ ] `chitty guide work` and `chitty guide review` say this, `PLAN.md` records the decision, and `__version__` is bumped above `main`'s

## History

- 2026-11-05T14:43:41Z mellow-newt → backlog
- 2026-11-05T14:47:45Z mellow-newt: changed title, dependencies, description
