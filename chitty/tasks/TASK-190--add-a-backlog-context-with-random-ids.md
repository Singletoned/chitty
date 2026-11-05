---
title: Add a `BACKLOG` context with random IDs
status: todo
priority: high
owner: human
depends_on:
  - TASK-177
parent: TASK-106
created: 2026-11-05
---

## Description

First of three parts. The human decided on 2026-11-05 that tickets raised by workers and reviewers should go to backlog with a separate, non-sequential ID, and be assessed in the planning session, which turns them into normally numbered tickets later. Then only `main` hands out sequential numbers. This supersedes `TASK-61`, which reached the same place through the inbox.

This part adds the context and its IDs. Add `random_ids: bool` to `ContextConfig` in `src/chitty/config.py`, named for its effect. A context with it gets random numbers from 10000000 to 99999999, such as `BACKLOG-48213907`: `ID_RE` needs a first digit of 1 to 9, and `TaskId` holds an integer, so this needs no change to it, its ordering, filenames or `ID_RE`. In `Repo.next_number` call a module-level `_random_number()` using `secrets.randbelow`, which a test can patch, retrying a bounded number of times if a known ticket uses the number, and raising a `ChittyError` if none is free. Check against the same set of numbers `next_number` gains in `TASK-177` from `self._history()`, so other branches' tickets count.

Add a `backlog` context with prefix `BACKLOG` and `random_ids = true` to `INITIAL_CONFIG`. `chitty init` must add it to existing repositories: `_add_missing_settings` in `src/chitty/store.py` only adds top-level keys, so write a function like `_add_missing_human_review`. In `pyproject.toml` insert after the last `[tool.chitty.contexts.*]` table, not at the end of the file, with a blank line before it and a following table header kept separate. If no such header is found, as with dotted keys, skip. Skip it when a `backlog` context or `BACKLOG` prefix already exists, or `RepoConfig._consistent` rejects the result. `ContextConfig` forbids extra keys, so an older Chitty refuses a file with this setting. That is accepted: `chitty_version` already says it needs upgrading.

The name collides with nothing: `chitty/backlog/` is a new directory, and the status `backlog` is a separate namespace. `chitty next` skips the status, and `list` and sorting cope with 8-digit numbers. Tests add `backlog` to their own configuration, not the shared `CONFIG` in `tests/support.py`. Bumping `__version__` means the next Chitty write on the branch upgrades this repository's own `chitty.toml` through `_prepare_write`, adding the context: commit that.

Out of scope: when a ticket uses this context, which is the next two parts; IDs made of words, as in `BACKLOG-ember-dolphin-1`, because `TaskId.number` is an integer used throughout; and any change to `TASK-` numbering.

## Acceptance Criteria

- [ ] A test with `_random_number` patched shows `chitty add -c backlog` creating `BACKLOG-<number>`, retrying when the number is already used, including on another branch, and raising when none is free
- [ ] Tests show `chitty init` adding the context to an existing `chitty.toml` and `pyproject.toml`, leaving a repository alone when it already has one, and `chitty check` passing with these tickets present
- [ ] `__version__` is bumped above `main`'s, and `README.md` and `PLAN.md` describe the setting

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. It was too big, so split in three, and this is the first. Fixed here: how a table gets added to existing files, a leading zero, and how to test retrying. The tickets following this hold the status rules and the default.

Cold read of the split by a fresh Sonnet subagent, 2026-11-05. Fixed: which numbers the retry checks, how the table is inserted, and where tests configure it. Rejected: leaving this repository's `chitty.toml` to `TASK-192`, because `_prepare_write` upgrades it at the next write after the bump.

Owner set to human only so chitty run leaves this ticket to this session; cleared when it goes to review.

## History

- 2026-11-05T14:43:41Z mellow-newt → backlog
- 2026-11-05T14:47:45Z mellow-newt: changed title, dependencies, description
- 2026-11-05T14:47:46Z mellow-newt: changed acceptance criteria
- 2026-11-05T14:47:47Z mellow-newt: changed acceptance criteria
- 2026-11-05T14:47:48Z mellow-newt: changed acceptance criteria
- 2026-11-05T14:47:49Z mellow-newt: changed acceptance criteria
- 2026-11-05T14:47:50Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T14:50:37Z mellow-newt: changed description, notes
- 2026-11-05T14:50:38Z mellow-newt backlog → todo
- 2026-11-05T21:14:08Z youthful-toad: changed owner, notes
