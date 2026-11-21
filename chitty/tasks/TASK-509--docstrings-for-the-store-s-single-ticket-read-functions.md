---
title: Docstrings for the store's single-ticket read functions
status: review
labels:
  - untestable
owner: nimble-umber-adder
parent: TASK-376
created: 2026-11-21
---

## Description

Add short docstrings to `source_copy`, `_choose_source`, `lookup`, `find`, `context_of`, `all_tasks`, and `_tasks_in_location` in `src/chitty/store.py`. Previous planning misdescribed these helpers. Document the code as it stands; change no runtime behavior and add no tests for wording. Run `make check`.

For single-ticket reads, point to `ticket_source` (directly or through the helper that calls it) for authoritative source selection. State which helper picks a source without checking whether a copy exists, which parses the selected copy, how missing tickets are reported, and how `context_of` uses the selected path or the configured prefix without parsing. For bulk reads, describe the separate history and working-tree overlay, cache, scope (configured contexts for `all_tasks`), which inputs are parsed, and empty results.

Document store-level and source-policy `ChittyError` cases with their message prefixes or templates where raised, using cross-references for callers that propagate them. Distinguish discovery/scan failures, duplicate files at the selected source, local and ref parse errors, source-policy failures, and the no-context and no-task cases. Summarize propagated Git and configuration failures without enumerating lower-level messages. Do not link to `docs/plan/ticket-state.md` until it exists in the checkout.

## Plan

Document the seven helpers in place. Use `ticket_source` for single-ticket selection and `_tasks_in_location` for the bulk listing contract. Put error prefixes at the helper that raises or first exposes them, and cross-reference them in wrappers. Run formatting and the full check; verify the diff only changes docstrings.

## Notes

The required reference `docs/plan/ticket-state.md` is not in this worktree or its main base. It exists on `plan/ticket-state`, and `TASK-387` is still todo and explicitly calls for landing it. Decide whether to depend on `TASK-387` or use `chitty.ticket_source.ticket_source` as the sole reference for now; do not add a link to a missing file.

The requested common source-selection description does not fit all seven functions. `all_tasks` visits active and archived directories for configured contexts; `_tasks_in_location` uses a cache or parses local files and matching historical records from `git.historical_files`, picks by commit time per ID and overlays eligible local copies. Neither calls `ticket_source`, so they need separate bulk-read wording. Both return lists, including an empty list when nothing matches. `context_of` uses the first selected path without parsing content or rejecting duplicate copies, then can return a configured prefix match even when the ticket is absent; it raises `<ID>: no context` if there is no fallback. `_choose_source` can return a source with no file for the requested ID; it does not parse ticket bodies. `find` raises `no task <ID>` only if context lookup succeeds on a miss.

Please also clarify whether “every `ChittyError`” means ticket-specific errors with prefixes plus a short statement that operational errors propagate, or an exhaustive inventory including transitive Git, configuration and discovery failures. The latter conflicts with short docstrings and repeats lower-level contracts. Selection, scanning and parsing errors differ: for example, local failures use `<path>: <error>`, ref parse failures use `<ref>:<path>: <error>`, and single-ticket discovery can fail on a bad filename unrelated to the requested ID before selection. No source files changed and `make check` was not run.

## Summary

Documented all seven store read helpers in `src/chitty/store.py`. Single-ticket reads reference `ticket_source`; bulk reads describe the history and working-tree overlay. The docstrings distinguish missing results, parse and discovery errors, and source-policy failures. The missing design doc is not linked. The AST is unchanged with docstrings removed, and `make check` passed (974 tests).

## History

- 2026-11-21T14:32:02Z sunny-ebony-kestrel → todo
- 2026-11-21T16:07:03Z nimble-umber-adder: changed owner; wrote the plan
- 2026-11-21T16:07:03Z nimble-umber-adder todo → doing
- 2026-11-21T16:07:39Z nimble-umber-adder: changed owner, notes
- 2026-11-21T16:07:39Z nimble-umber-adder doing → planning
- 2026-11-21T16:09:12Z nimble-umber-adder: changed owner, description
- 2026-11-21T16:09:12Z nimble-umber-adder planning → todo
- 2026-11-21T16:09:16Z nimble-umber-adder: changed owner; wrote the plan
- 2026-11-21T16:09:16Z nimble-umber-adder todo → doing
- 2026-11-21T16:12:30Z nimble-umber-adder: changed summary
- 2026-11-21T16:12:30Z nimble-umber-adder doing → review
