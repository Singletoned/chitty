---
title: Docstrings for the store's single-ticket read functions
status: planning
labels:
  - untestable
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

## Notes

The required reference `docs/plan/ticket-state.md` is not in this worktree or its main base. It exists on `plan/ticket-state`, and `TASK-387` is still todo and explicitly calls for landing it. Decide whether to depend on `TASK-387` or use `chitty.ticket_source.ticket_source` as the sole reference for now; do not add a link to a missing file.

The requested common source-selection description does not fit all seven functions. `all_tasks` visits active and archived directories for configured contexts; `_tasks_in_location` uses a cache or parses local files and matching historical records from `git.historical_files`, picks by commit time per ID and overlays eligible local copies. Neither calls `ticket_source`, so they need separate bulk-read wording. Both return lists, including an empty list when nothing matches. `context_of` uses the first selected path without parsing content or rejecting duplicate copies, then can return a configured prefix match even when the ticket is absent; it raises `<ID>: no context` if there is no fallback. `_choose_source` can return a source with no file for the requested ID; it does not parse ticket bodies. `find` raises `no task <ID>` only if context lookup succeeds on a miss.

Please also clarify whether “every `ChittyError`” means ticket-specific errors with prefixes plus a short statement that operational errors propagate, or an exhaustive inventory including transitive Git, configuration and discovery failures. The latter conflicts with short docstrings and repeats lower-level contracts. Selection, scanning and parsing errors differ: for example, local failures use `<path>: <error>`, ref parse failures use `<ref>:<path>: <error>`, and single-ticket discovery can fail on a bad filename unrelated to the requested ID before selection. No source files changed and `make check` was not run.

## History

- 2026-11-21T14:32:02Z sunny-ebony-kestrel → todo
- 2026-11-21T16:07:03Z nimble-umber-adder: changed owner; wrote the plan
- 2026-11-21T16:07:03Z nimble-umber-adder todo → doing
- 2026-11-21T16:07:39Z nimble-umber-adder: changed owner, notes
- 2026-11-21T16:07:39Z nimble-umber-adder doing → planning
