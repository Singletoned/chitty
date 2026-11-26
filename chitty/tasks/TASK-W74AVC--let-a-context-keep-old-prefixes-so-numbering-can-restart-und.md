---
title: Let a context keep old prefixes so numbering can restart under a new one
status: cold-read
labels:
  - needs-minor
created: 2026-11-26
provisional: true
---

## Description

### Why

Ticket numbers grow without bound; this repository's jumped to `TASK-10000`. The person asked for "a number bankruptcy system where we start again", and chose (2026-11-26) to start under a new prefix rather than reuse numbers: every old ID stays unique, so commit messages, `task-<n>` branch names and other repositories' citations stay correct, and nothing is rewritten.

### Change

Add `old_prefixes` (a list of prefixes, default empty) to `ContextConfig` in `src/chitty/config.py`, validated like `prefix`. `RepoConfig`'s check that no prefix belongs to two contexts covers old prefixes as well, and an old prefix may not equal its own context's `prefix`. `Context` in `src/chitty/store.py` gets the same field, filled in `Repo.context`.

Tickets with an old prefix stay readable and linkable, but new IDs use only `prefix`:

- `scan` accepts files whose prefix is the context's `prefix` or one of its `old_prefixes`.
- `Repo.context_of` falls back to a context whose `prefix` or `old_prefixes` matches.
- The prefix sets used to find ticket branches (`Repo` around the `prefixes = {context.prefix ...}` line near `ref != main_ref`), to find references in text (`referenced_tasks`), and in `_remove_merged_branches` include old prefixes.
- Numbering (`_used_numbers`, `new_id`, provisional renumbering) counts only the current `prefix`, so the new prefix starts at 1. Bare numbers in commands (`Repo.resolve`) keep meaning the default context's current `prefix`.

Starting again is then a config change made on `main` by a person: set `prefix` to the new prefix and add the old one to `old_prefixes`. Document this in `docs/plan/config.md`.

### Out of scope

A command that changes the prefix; renaming old tickets; other repositories' references.

## Acceptance Criteria

- [ ] In a new `tests/test_old_prefixes.py` (`CliTestCase`), with tickets `TASK-1` and `TASK-2` (`TASK-2` depending on `TASK-1`) and an open branch `task-2`, then the `tasks` context changed in `chitty.toml` to `prefix = "TK"` and `old_prefixes = ["TASK"]`: `chitty check` reports no problems; `chitty show TASK-1` works; `chitty add New -d Text.` creates `TK-1`; `chitty edit TK-1 --depends-on TASK-2` succeeds; and `chitty edit TK-1 -s todo` lists `TASK-2` as a referenced ticket. Fails without the change.
- [ ] Configuration validation (in the existing config tests) refuses `old_prefixes` entries that are not upper-case letters, that equal the context's own `prefix`, or that another context uses as its `prefix` or in its `old_prefixes`, each with an error naming the prefix. Fails without the change.
- [ ] The runner's merged-branch cleanup (`_remove_merged_branches` in `src/chitty/run.py`) removes a merged `task-<n>` branch whose ticket uses an old prefix, as it does for the current prefix (extend its existing test). `make check` passes.

## History

- 2026-11-26T11:11:53Z calm-ochre-quail → backlog
- 2026-11-26T17:50:32Z calm-ochre-quail: changed title, labels, description, acceptance criteria
- 2026-11-26T17:50:32Z calm-ochre-quail backlog → cold-read
