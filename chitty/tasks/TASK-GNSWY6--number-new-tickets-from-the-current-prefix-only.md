---
title: Number new tickets from the current prefix only
status: cold-read
depends_on:
  - TASK-MQ87S9
parent: TASK-W74AVC
created: 2026-11-26
provisional: true
---

## Description

### Why

Part of TASK-W74AVC: after a person changes a context's `prefix` (TASK-MQ87S9), new tickets should start again at 1. Today `Repo._used_numbers` (`src/chitty/store.py`) collects the number of every file in the context whatever its prefix (`_files` scans with `allow_any_prefix=True`), so `ids.next_number` continues after the old tickets.

### Change

In `_used_numbers`, count only files whose ID prefix is the context's current `prefix`, as `_deleted_numbers` and the provisional branch of `new_id` already do. The renumbering `used` map is built from `_used_numbers`, so it follows. Mentions of old-prefix IDs never affect the new prefix's numbers, since they have another prefix.

### Out of scope

Reading old-prefix tickets (sibling ticket); random-ID contexts.

## Acceptance Criteria

- [ ] In `tests/test_old_prefixes.py` (no Git is needed), with tickets `TASK-1` to `TASK-3` and the `tasks` context then changed to `prefix = "TK"` and `old_prefixes = ["TASK"]`: `chitty add New -d Text.` creates `TK-1`, and a second add creates `TK-2`. Fails without the change (today `TK-4`).
- [ ] In `tests/test_renumber_provisional.py`, on `main` with the same setup and one provisional `TK-` ticket (`provisional: true` written into its file directly), bare `chitty renumber` gives it `TK-1`. Fails without the change. Regression tests: the existing numbering and renumbering tests pass. `make check` passes.

## History

- 2026-11-26T17:52:22Z calm-ochre-quail → cold-read
