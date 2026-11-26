---
title: Number new tickets from the current prefix only
status: todo
parent: TASK-10053
created: 2026-11-26
moved_from: TASK-GNSWY6
---

## Description

### Why

Part of TASK-10053: after a person changes a context's `prefix` (TASK-10048), new tickets should start again at 1. Today `Repo._used_numbers` (`src/chitty/store.py`) collects the number of every file in the context whatever its prefix (`_files` scans with `allow_any_prefix=True`), so `ids.next_number` continues after the old tickets.

### Change

In `_used_numbers`, count only files whose ID prefix is the context's current `prefix`, as `_deleted_numbers` and the provisional branch of `new_id` already do. The renumbering `used` map is built from `_used_numbers`, so it follows. Mentions of old-prefix IDs never affect the new prefix's numbers, since they have another prefix.

### Out of scope

Reading old-prefix tickets (sibling ticket). The filter applies to random-ID contexts too, which is correct: a random ID collides only on its full prefix and number.

## Acceptance Criteria

- [ ] In `tests/test_old_prefixes.py` (create it or add to it; no Git is needed), with tickets `TASK-1` to `TASK-3` and the `tasks` context then changed in `chitty.toml` to `prefix = "TK"` (no `old_prefixes` needed): `chitty add New -d Text.` creates `TK-1`, and a second add creates `TK-2`. Fails without the change (today `TK-4`).
- [ ] In `tests/test_renumber_provisional.py`, outside Git with the same setup and one provisional ticket file `TK-AAAAAA--alpha.md` (`provisional: true`, as `TestRenumberOutsideGit.setUp` writes `TASK-AAAAAA`), bare `chitty renumber` gives it `TK-1`. Fails without the change. Regression tests: the existing numbering and renumbering tests pass. `make check` passes.

## History

- 2026-11-26T17:52:22Z calm-ochre-quail → cold-read
- 2026-11-26T17:54:10Z calm-ochre-quail: changed dependencies, description, acceptance criteria
- 2026-11-26T17:54:10Z calm-ochre-quail cold-read → todo
- 2026-11-26T20:30:10Z intrepid-russet-falcon: renumbered from TASK-GNSWY6
