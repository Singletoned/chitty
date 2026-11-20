---
title: Read ticket listings from each ticket's authoritative source, not every ref's history
status: backlog
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-20
---

## Description

This ticket needs refining.

## Notes

Placeholder from the 2026-11-20 split of `TASK-378`; plan it after `TASK-378` lands. Scope: switch `_tasks_in_location` (so `tasks`, `all_tasks` and `chitty list`) to `ticket_ids()` plus `source_copy`, and apply the rule decided with the owner on 2026-11-20: an operation fails only if it needs the conflicted ticket's content. Isolated: `add` (free IDs only; `new_id` on a ticket branch uses `ticket_ids()`), `move <ID>` and `archive <ID>` (fail only when `<ID>` is the conflicted ticket). Fail naming the conflicted ticket: `list`, `archive` with no ID, and `renumber`. Also take over the former `TASK-378` criterion 4: with `git.historical_files` patched to raise, `chitty list` and `chitty show` still work, and outside Git `chitty list` reads the working tree.

Open decision for this ticket: `chitty show` lists a ticket's children through `all_tasks()` (`src/chitty/cli.py`, `show`), which needs every ticket's `parent`, which is content. After the switch, one conflicted ticket would make `show` of any ticket fail. Decide whether `show` skips the conflicted ticket when listing children, with a warning naming it, or fails.

Also: `_collect_ticket_ids` reads the content of every ticket file on `main` and on each ticket branch (`git.files_at`); check `tests/test_list_performance.py` against that.

## History

- 2026-11-20T22:59:14Z quick-pearl-lapwing → backlog
- 2026-11-20T22:59:58Z quick-pearl-lapwing: changed notes
