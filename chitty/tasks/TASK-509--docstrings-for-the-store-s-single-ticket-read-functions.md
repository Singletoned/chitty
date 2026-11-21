---
title: Docstrings for the store's single-ticket read functions
status: doing
labels:
  - untestable
owner: nimble-umber-adder
parent: TASK-376
created: 2026-11-21
---

## Description

On 2026-11-21 several tickets were returned because their planners misdescribed these functions. None of them has a docstring. Add one to each in `src/chitty/store.py`: `source_copy`, `_choose_source`, `lookup`, `find`, `context_of`, `all_tasks` and `_tasks_in_location`.

Each docstring states, from the code as it is when you write it (check it; do not copy this list):

- which copy it reads (working tree, `main`, a ticket branch or a remote-tracking ref) and by what rule, pointing to `ticket_source` and `docs/plan/ticket-state.md` rather than restating the rule;
- whether it parses ticket content, and which content (for example, `_choose_source` parses nothing; `source_copy` parses only the chosen copy; `all_tasks` and `_tasks_in_location` parse every file they list);
- what it returns when there is no ticket (`None`, or which error);
- every `ChittyError` it can raise, with the message's start, for example `is used by more than one file`, `changed on both`, a diverged-refs error, `configured main branch ... has no tip`, and a parse error formatted `<ref>:<path>: <error>`.

Keep each docstring short: a summary line, then the points above as plain sentences. Do not change behaviour. `make check` passes.

## Plan

Trace all seven store helpers and their dependencies. Compare single-ticket source selection with bulk listing, then document their parsing, absence and errors without changing behavior. Verify the selection rules against the design docs and run formatting and checks if implementation proceeds.

## History

- 2026-11-21T14:32:02Z sunny-ebony-kestrel → todo
- 2026-11-21T16:07:03Z nimble-umber-adder: changed owner; wrote the plan
- 2026-11-21T16:07:03Z nimble-umber-adder todo → doing
