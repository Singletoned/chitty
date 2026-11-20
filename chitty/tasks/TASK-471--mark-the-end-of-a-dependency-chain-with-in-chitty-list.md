---
title: Mark the end of a dependency chain with 🚧 in `chitty list`
status: todo
priority: high
parent: TASK-70
created: 2026-11-20
---

## Description

Seen 2026-11-20: 12 `todo` tickets waited (🔗) on tickets still in `planning`, so `chitty run --mode work` found nothing to do, but `chitty list` gave no sign that `TASK-378` alone held up 7 of them. A planner should see which tickets to plan first: the ones at the end of a chain, which others wait on and which wait on nothing themselves.

Decisions (owner, 2026-11-20):

- New marker `🚧` in the existing marker column of text `chitty list`. Add the module constant `BLOCKER_GLYPH = "🚧"` in `src/chitty/selection.py`. No count and no new column.
- A ticket is a blocker when it is not archived, not `done`, has no `unfinished` or `broken` dependency of its own, and at least one waiting dependent names it. A waiting dependent is a ticket that is not archived, not `done`, and has a dependency fact with that reference and state `unfinished`. References compare as `str(TaskId.parse(reference))`, so a hand-written `task-1` names `TASK-1`. Direct dependents only. Owner, lock and context do not change whether a ticket is a blocker or a waiting dependent; they only change which marker wins (below). A dependent with a `broken` dependency still names its `unfinished` ones (`_selection_facts` stops at the first `broken` dependency, so only those before it exist). A blocked ticket in the middle of a chain shows its `🔗` as today.
- Dependents count whatever the list filters: build facts for every active ticket in `repo.discovered_contexts()`, not only the listed ones, so `chitty list -s planning` still marks a planning blocker whose dependents are `todo`.
- New pure functions in `src/chitty/selection.py`: `blocking_ids(facts: Iterable[TicketFacts]) -> set[str]`, the references named by waiting dependents; and `blocker_marker(fact: TicketFacts, blocking: Set[str]) -> str | None`, `BLOCKER_GLYPH` when `fact` is a blocker by the rule above, else `None`.
- `src/chitty/store.py`: new `blocking_ids_for(repo: Repo) -> set[str]` builds the facts with `_selection_facts(repo, stored, locked=False, dependencies=True)` and calls `blocking_ids`. `list_marker` takes a third parameter `blocking: Set[str]` and, after `skip_reason` and `dependency_marker` both give `None`, returns `blocker_marker` of the same facts. Running, human, owner (`👤`, `✍️`), `🔗` and `⚠️` markers keep precedence. `chitty list` in `src/chitty/cli.py` computes `blocking_ids_for(repo)` once and passes it to every `list_marker` call.
- Docs: describe `🚧` and its precedence in `README.md` (near line 97), `docs/plan/cli.md` (lines 46 to 52) and `docs/plan/next-action-and-runner.md` (line 16). Existing tests that assert full `chitty list` lines (for example in `tests/test_cli.py`) change only where a listed ticket meets the blocker rule.
- Out of scope: `chitty list --json` (`skipped` is unchanged), `chitty next`, `chitty run`, `chitty show`, list ordering, and transitive counts.

Dependency reads are memoised (`_dependency_is_done` in `src/chitty/store.py` reads `main` once through `_main_files_for`), so this should add no Git calls per ticket; `tests/test_list_performance.py` checks the call count.

## Acceptance Criteria

- [ ] New file `tests/test_property_blockers.py`: a Hypothesis property over lists of `TicketFacts` with unique IDs drawn from `TASK-1` to `TASK-6`, status from `chitty.model.STATUSES` (not the shorter tuple in `selection.py`), random `archived` and `locked`, `owner` from `None`, `agent`, `human` and `untestable`, `context` from `work` and `human`, and up to three dependencies each with a reference drawn from `TASK-1` to `TASK-6` (never the ticket itself) or `TASK-99`, written upper- or lowercase, and a state from `done`, `unfinished` and `broken`, where a `broken` one, if any, is last (as `_selection_facts` builds them). For every fact, `blocker_marker(fact, blocking_ids(facts))` equals an independently written expectation of the rule in the Description, and `blocking_ids` of a shuffled copy equals `blocking_ids` of the list. It fails on `main` (stub both functions raising `NotImplementedError` first). Run these wrong versions and record in a note which example failed: one that also marks a ticket with an `unfinished` dependency; one that counts `done` or archived dependents; one that counts dependency facts in state `done`; one that skips owned or locked dependents; one that compares raw references.
- [ ] New file `tests/test_list_blockers.py` commits these tickets to `main` before listing (so `_dependency_is_done` reads `main`, not the working tree): `TASK-1` `planning` titled `Blocker one` with no dependencies; `TASK-2` `todo` depending on `TASK-1`; `TASK-3` `planning` depending on `TASK-1` and `TASK-2`; `TASK-4` `done` depending on `TASK-5`; `TASK-5` `planning` with no dependencies; `TASK-6` `doing` with owner `agent`; `TASK-7` `todo` depending on `TASK-6`; `TASK-8` `backlog` depending on `TASK-9`; `TASK-9` `blocked` with no dependencies. It asserts every `chitty list --all` line in full as literal strings, like the full-line list tests in `tests/test_cli.py`: `🚧` for `TASK-1` and `TASK-9`, `🔗` for `TASK-2`, `TASK-3`, `TASK-7` and `TASK-8`, `👤` for `TASK-6`, and an empty marker for `TASK-4` and `TASK-5`. `chitty list -s planning` and `chitty list --search "Blocker one"` still show `🚧` for `TASK-1`, and `chitty list --json` gives `skipped` `None` for `TASK-1`. It fails on `main`.
- [ ] `tests/test_list_performance.py` changes `_task` to take a list of dependencies, gives each dependent `depends_on` `[TASK-1, TASK-1000]`, adds a `planning` ticket `TASK-1000` with no dependencies, asserts its `chitty list` line shows `🚧`, and still asserts the same Git call count for both ticket counts. Run a wrong version of `blocking_ids_for` that clears `repo._main_files` (the memo `_main_files_for` uses, `src/chitty/store.py` line 372) before each ticket, and record in a note that the test fails. The Docs decision is done. `make check` passes.

## History

- 2026-11-20T08:02:18Z lively-bronze-crane → planning
- 2026-11-20T08:02:37Z lively-bronze-crane: changed acceptance criteria
- 2026-11-20T08:02:41Z lively-bronze-crane planning → cold-read
- 2026-11-20T08:04:35Z lively-bronze-crane cold-read → planning
- 2026-11-20T08:04:38Z lively-bronze-crane: changed description, acceptance criteria
- 2026-11-20T08:04:47Z lively-bronze-crane: changed acceptance criteria
- 2026-11-20T08:04:51Z lively-bronze-crane planning → cold-read
- 2026-11-20T08:06:25Z lively-bronze-crane cold-read → planning
- 2026-11-20T08:06:27Z lively-bronze-crane: changed description, acceptance criteria
- 2026-11-20T08:06:31Z lively-bronze-crane planning → todo
