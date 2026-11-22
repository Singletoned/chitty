---
title: Escape lone literal asterisks in `chitty suggest` descriptions
status: todo
labels:
  - bug
priority: high
depends_on:
  - TASK-529
parent: TASK-348
created: 2026-11-21
---

## Description

Split from `TASK-348` on 2026-11-21. After `TASK-529`, `new_task` escapes lone literal asterisks. `suggest` in `src/chitty/inbox.py` validates the normalized description through `new_task` and raises if the result differs (lines 40-44 on 2026-11-21), so it would refuse a description that needs escaping; it then writes the raw `description` argument to the suggestion file (lines 71-72). `TASK-529` landed on 2026-11-22, and since then `chitty suggest` refuses such descriptions (probe: `suggestion Description does not round-trip through task storage` for ``files/*.jpg and `x*y` ``), so this is a regression to fix promptly.

Decided 2026-11-21: in `suggest`, apply `escape_literal_asterisks` to the normalized description before building the candidate, and, when a description was given (today's `if description:` at line 71), write that escaped normalized text (not the raw argument) to the suggestion file. A suggestion with no description keeps today's output: no Description section is written, even though `normalized` falls back to `BACKLOG_DESCRIPTION` for the check. The round-trip check then compares escaped with escaped. `pull` reaches `new_task` through `repo.add`; escaping is idempotent, so the second pass changes nothing.

Test `test_suggestion_description_escapes_literal_asterisks` in `tests/test_inbox.py`, in the style of `test_suggestion_is_written_to_this_test_inbox`: `chitty suggest` with description ``files/*.jpg and `x*y` `` succeeds, the suggestion file holds ``files/\*.jpg and `x*y` ``, and `chitty inbox --pull` creates a ticket whose Description is that escaped text.

## Acceptance Criteria

- [ ] `test_suggestion_description_escapes_literal_asterisks` passes, and fails before the change with `suggestion Description does not round-trip through task storage` (record the failing run in a note)
- [ ] The existing `tests/test_inbox.py` and `tests/test_property_inbox.py` tests pass, including suggestions with no description; `make check` passes

## History

- 2026-11-21T23:22:19Z lively-zinc-newt → planning
- 2026-11-22T01:19:41Z lively-zinc-newt: changed labels, priority, description
- 2026-11-22T01:19:41Z lively-zinc-newt planning → cold-read
- 2026-11-22T01:20:22Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T01:20:22Z lively-zinc-newt cold-read → todo
