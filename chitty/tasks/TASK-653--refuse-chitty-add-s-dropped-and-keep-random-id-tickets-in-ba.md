---
title: Refuse `chitty add -s dropped`, and keep random-ID tickets in `backlog`
status: planning
priority: high
depends_on:
  - TASK-599
parent: TASK-599
created: 2026-11-24
---

## Description

`TASK-599` added the `dropped` status. Creating a ticket as `dropped` makes no sense (it is closed before anyone sees it, and `chitty add` has no `--summary` for the reason `TASK-652` requires), so refuse it.

Change, in `Repo.add` in `src/chitty/store.py`: when the requested status is `dropped`, raise `ChittyError` `create the ticket, then drop it with chitty edit -s dropped --summary` before anything is written. Put the check before the line that forces a random-ID context's ticket to `backlog`, so `chitty add -c backlog -s dropped` is refused too rather than silently creating a `backlog` ticket.

Random-ID contexts keep their rule that every ticket there is `backlog` (decided with the person, 2026-11-23; contexts are being removed by `TASK-262` and `TASK-267`): the existing check in `Repo._edit_stored` already refuses `-s dropped` there, and the regression test pins that.

Tests: add to the existing `tests/test_status_dropped.py`. For the random-ID cases, add the `BACKLOG` context table as `tests/test_backlog_context.py` does; the add refusal happens before an ID is drawn, so only the `edit` case needs its `_random_number` patch. The random-ID guard runs early in `_edit_stored`, before `TASK-652`'s post-edit Summary check, so the regression test keeps its message either way. No property: two fixed cases.

Out of scope: `chitty edit` rules for dropping (`TASK-652`), archiving (`TASK-654`).

## Acceptance Criteria

- [ ] `chitty add T -d x -s dropped` and `chitty add Idea -c backlog -s dropped` are each refused with `create the ticket, then drop it with chitty edit -s dropped --summary` and create no file; both fail before the change
- [ ] Regression tests: `chitty edit <id> -s dropped --summary x` on a `backlog`-context ticket is refused with a message containing `chitty move <id> tasks` and a byte-identical file; `make check` passes

## History

- 2026-11-24T08:45:27Z sunny-hazel-gannet → planning
- 2026-11-24T09:27:45Z sunny-hazel-gannet: changed dependencies
- 2026-11-24T22:32:17Z sunny-hazel-gannet: changed notes
- 2026-11-26T19:00:12Z zesty-ginger-newt: changed notes
- 2026-11-26T19:00:12Z zesty-ginger-newt planning → to-plan
- 2026-11-26T19:00:20Z zesty-ginger-newt: replaced notes; changed dependencies, description, acceptance criteria
- 2026-11-26T19:00:20Z zesty-ginger-newt to-plan → planning
- 2026-11-26T19:00:29Z zesty-ginger-newt planning → cold-read
- 2026-11-26T19:05:19Z zesty-ginger-newt: changed description
- 2026-11-26T19:05:19Z zesty-ginger-newt cold-read → planning
