---
title: Mark the end of a dependency chain with 🚧 in `chitty list`
status: planning
priority: high
parent: TASK-70
created: 2026-11-20
---

## Description

Seen 2026-11-20: 12 `todo` tickets waited (🔗) on tickets still in `planning`, so `chitty run --mode work` found nothing to do, but `chitty list` gave no sign that `TASK-378` alone held up 7 of them. A planner should see which tickets to plan first: the ones at the end of a chain, which others wait on and which wait on nothing themselves.

Decisions (owner, 2026-11-20):

- New marker `🚧` in the existing marker column of text `chitty list`. Add the module constant `BLOCKER_GLYPH = "🚧"` in `src/chitty/selection.py`. No count and no new column.
- A ticket is a blocker when it is not archived, not `done`, has no `unfinished` or `broken` dependency of its own, and at least one waiting dependent names it. A waiting dependent is a ticket that is not archived, not `done`, and has a dependency fact with that reference and state `unfinished`. Direct dependents only. A blocked ticket in the middle of a chain shows its `🔗` as today. No status other than `done` is named, as for `dependency_marker`.
- Dependents count whatever the list filters: build facts for every active ticket in `repo.discovered_contexts()`, not only the listed ones, so `chitty list -s planning` still marks a planning blocker whose dependents are `todo`.
- New pure functions in `src/chitty/selection.py`: `blocking_ids(facts: Iterable[TicketFacts]) -> set[str]`, the references named by waiting dependents; and `blocker_marker(fact: TicketFacts, blocking: Set[str]) -> str | None`, `BLOCKER_GLYPH` when `fact` is a blocker by the rule above, else `None`.
- `src/chitty/store.py`: new `blocking_ids_for(repo: Repo) -> set[str]` builds the facts with `_selection_facts(repo, stored, locked=False, dependencies=True)` and calls `blocking_ids`. `list_marker` takes a third parameter `blocking: Set[str]` and, after `skip_reason` and `dependency_marker` both give `None`, returns `blocker_marker` of the same facts. Running, human, owner (`👤`, `✍️`), `🔗` and `⚠️` markers keep precedence. `chitty list` in `src/chitty/cli.py` computes `blocking_ids_for(repo)` once and passes it to every `list_marker` call.
- Out of scope: `chitty list --json` (`skipped` is unchanged), `chitty next`, `chitty run`, `chitty show`, list ordering, and transitive counts.

Dependency reads are memoised (`_dependency_is_done` in `src/chitty/store.py` reads `main` once through `_main_files_for`), so this should add no Git calls per ticket; `tests/test_list_performance.py` checks the call count.

## Acceptance Criteria

- [ ] New file `tests/test_property_blockers.py`: a Hypothesis property over lists of `TicketFacts` with unique IDs drawn from `TASK-1` to `TASK-6`, any status from `STATUSES` in `src/chitty/model.py`, random `archived`, and up to three dependencies each with a reference drawn from `TASK-1` to `TASK-6` or `TASK-99` and a state from `done`, `unfinished` and `broken`. For every fact, `blocker_marker(fact, blocking_ids(facts))` equals an independently written expectation of the rule in the Description. It fails on `main` (stub both functions raising `NotImplementedError` first). Run these wrong versions and record in a note which example failed: one that also marks a ticket with an `unfinished` dependency; one that counts `done` or archived dependents; one that counts dependency facts in state `done`.
- [ ] New file `tests/test_list_blockers.py` builds: `TASK-1` `planning` with no dependencies; `TASK-2` `todo` depending on `TASK-1`; `TASK-3` `planning` depending on `TASK-1` and `TASK-2`; `TASK-4` `done` depending on `TASK-5`; `TASK-5` `planning` with no dependencies; `TASK-6` `doing` with owner `agent`; `TASK-7` `todo` depending on `TASK-6`. It asserts every `chitty list --all` line in full: `🚧` for `TASK-1`, `🔗` for `TASK-2`, `TASK-3` and `TASK-7`, `👤` for `TASK-6`, and a blank marker for `TASK-4` and `TASK-5`. `chitty list -s planning` still shows `🚧` for `TASK-1`, and `chitty list --json` gives `skipped` `None` for `TASK-1`. It fails on `main`.
- [ ] `tests/test_list_performance.py` makes its dependents also depend on an unfinished ticket and still asserts the same Git call count for both ticket counts. `README.md` (near line 97) and `docs/plan/cli.md` (lines 46 to 52) describe `🚧` and its precedence. `make check` passes.

## History

- 2026-11-20T08:02:18Z lively-bronze-crane → planning
- 2026-11-20T08:02:37Z lively-bronze-crane: changed acceptance criteria
- 2026-11-20T08:02:41Z lively-bronze-crane planning → cold-read
- 2026-11-20T08:04:35Z lively-bronze-crane cold-read → planning
