---
title: Escape lone literal asterisks in `chitty suggest` descriptions
status: planning
depends_on:
  - TASK-529
parent: TASK-348
created: 2026-11-21
---

## Description

Split from `TASK-348` on 2026-11-21. After `TASK-529`, `new_task` escapes lone literal asterisks. `suggest` in `src/chitty/inbox.py` validates the normalized description through `new_task` and raises if the result differs (lines 40-44 on 2026-11-21), so it would refuse a description that needs escaping; it then writes the raw `description` argument to the suggestion file (lines 71-72). Draft: keep in planning until `TASK-529` lands.

Decided 2026-11-21: in `suggest`, apply `escape_literal_asterisks` to the normalized description before building the candidate, and write that escaped normalized text (not the raw argument) to the suggestion file. The round-trip check then compares escaped with escaped. `pull` reaches `new_task` through `repo.add`; escaping is idempotent, so the second pass changes nothing.

Test in `tests/test_inbox.py`, in the style of `test_suggestion_is_written_to_this_test_inbox`: `chitty suggest` with description ``files/*.jpg and `x*y` `` succeeds, the suggestion file holds ``files/\*.jpg and `x*y` ``, and `chitty inbox --pull` creates a ticket whose Description is that escaped text.

## Acceptance Criteria

- [ ] The suggestion test stores and imports the escaped text, and fails before the change; `make check` passes

## History

- 2026-11-21T23:22:19Z lively-zinc-newt → planning
