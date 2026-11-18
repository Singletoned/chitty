---
title: Decide where each ticket is read from in a pure `ticket_source` function
status: cold-read
parent: TASK-376
created: 2026-11-18
---

## Description

Today Chitty answers "what is TASK-X now?" by scanning every ref's history and taking the copy with the newest commit time (`git.historical_files`, `Repo._tasks_in_location` in `src/chitty/store.py`). Commit time is not causal order, so it picks wrong copies. The decided rule (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`) picks one authoritative copy without timestamps. This ticket builds that rule as a pure function only; `TASK-378` wires it into `Repo`.

Decisions:

- New module `src/chitty/ticket_source.py`. Create it first with the names below, the function raising `NotImplementedError`, so the tests fail on behaviour rather than at import.
- `WORKING_TREE` is a module constant meaning "read this checkout's file". Otherwise the result is the short name of a ref (`task-5`, `origin/task-5`, `main`) whose tip holds the ticket.
- `ticket_source(task_id: TaskId, provisional: bool, current_branch: str | None, main_branch: str, local_tips: Mapping[str, str], remote_tips: Mapping[str, str], contains: Callable[[str, str], bool]) -> str`. `local_tips` maps every visible local branch name to its commit; `remote_tips` maps every visible remote-tracking branch (`origin/task-5`) to its commit; `contains(a, b)` is true when commit `a` has `b` in its history (true when equal). The function does no Git, file or clock access.
- The ticket branch name is `str(task_id).lower()` (`TASK-5` gives `task-5`, `HUMAN-12` gives `human-12`). Candidates are the local branch with exactly that name and every remote-tracking branch whose name after its first `/` is exactly that name. Other names (`task-50`, local `feature/task-5`, `origin/x/task-5`) are not candidates.
- Rules, in order:
  1. `provisional` true: `WORKING_TREE`.
  2. No candidates: `main` is authoritative. `WORKING_TREE` when `current_branch == main_branch`, else `main_branch`.
  3. Otherwise, the chosen tip is the candidate commit that contains every other candidate commit. Among candidates at that commit, the local branch wins, else the alphabetically first remote name. Result: `WORKING_TREE` when `current_branch` is the local candidate and its commit is the chosen one; else the chosen name.
  4. No candidate contains all the others (diverged): raise `ChittyError` whose message names every candidate.
- `current_branch` is `None` when `HEAD` is detached, including during a stopped rebase; the rules then never return `WORKING_TREE` except for a provisional ticket. Accepted: the ticket is read from its branch tip until the rebase finishes.
- A checkout knows only the branches it can see (a container may have only its own branch and `main`). The function treats its inputs as all there is.

Out of scope: any caller, reading files, and the write guard (`TASK-385`).

Tests: Hypothesis properties in a new `tests/test_property_ticket_source.py`. Generate a commit graph (each commit's parents drawn from earlier commits) with `contains` as reachability in it; a task ID with a random prefix and number; local and remote branch maps drawn from candidate names, decoy names (as listed above) and unrelated names, pointing at random commits; `current_branch` drawn from those names, `main_branch` and `None`; and `provisional`.

## Acceptance Criteria

- [ ] Properties pass for rules 1 and 2: a provisional ticket gives `WORKING_TREE` whatever the other inputs; with no candidates the result is `WORKING_TREE` exactly when `current_branch == main_branch`, else `main_branch`
- [ ] Properties pass for rule 3: whenever one candidate commit contains all the others, the result is `WORKING_TREE` exactly when `current_branch` is the local candidate at that commit, otherwise it names a candidate at that commit, the local one when it is there, else the alphabetically first remote
- [ ] Properties pass for rule 4 and decoys: when no candidate contains all the others, `ChittyError` is raised and its message contains every candidate name; adding or removing decoy and unrelated branches never changes the result
- [ ] Every property in `tests/test_property_ticket_source.py` fails against the `NotImplementedError` stub, and `make check` passes

## History

- 2026-11-18T16:20:02Z lively-quartz-crane → backlog
- 2026-11-18T16:21:15Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:21:15Z lively-quartz-crane backlog → planning
- 2026-11-18T16:21:24Z lively-quartz-crane planning → cold-read
