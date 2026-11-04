---
title: Let `chitty run` run a chosen ticket with `--ticket`
status: todo
priority: medium
depends_on:
  - TASK-126
parent: TASK-106
created: 2026-11-04
---

## Description

`chitty run` always takes what `chitty next` selects, so a person cannot choose. Add `chitty run --ticket <ID>`, which runs that ticket instead of the selected one, in the mode its status implies: `review` means review, and `doing` or `todo` means work. Everything else about the run is unchanged, including worktree preparation and forwarding other arguments to the agent.

Use an option rather than a positional argument. `chitty run` forwards unknown arguments to the agent, so a positional would be confused with those, as in `chitty run -e ./search.ts`.

Add a function beside `next_action` in `src/chitty/store.py` that returns a `NextAction` for a given ticket, sharing its eligibility rules rather than copying them; `run` and `cli.py` stay thin. It refuses, with a message saying why, and before any claim or worktree: an unknown or archived ticket; a status other than `review`, `doing` or `todo`; a `human` ticket or owner; and a `todo` ticket whose dependencies are not `done`. Choosing a ticket overrides priority and order only: the rules exist because the work would fail or belongs to someone else. To override one, change the ticket first.

Depends on `TASK-126`, which changes the command and `src/chitty/run.py`. `TASK-120` and `TASK-131` act on pending tickets at the start of a run, so a run with `--ticket` must only touch that ticket; they should keep to this if they land later, and this ticket should if they land first.

Out of scope: an option on `chitty next`, running several tickets, and overriding the refusals above.

## Acceptance Criteria

- [ ] A test with a fake agent shows `--ticket` running a lower-priority `todo` ticket in work mode ahead of what `chitty next` selects, and a `review` ticket in review mode
- [ ] Tests show each refused case failing with a message saying why, with no claim and no worktree created
- [ ] A test shows other arguments still reaching the agent alongside `--ticket`, and `chitty run` without it behaving as before
- [ ] `README.md` and `PLAN.md` describe the option

## History

- 2026-11-04T09:46:25Z lively-panda → todo
