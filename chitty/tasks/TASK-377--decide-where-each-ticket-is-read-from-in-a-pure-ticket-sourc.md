---
title: Decide where each ticket is read from in a pure `ticket_source` function
status: planning
parent: TASK-376
created: 2026-11-18
---

## Description

Today Chitty answers "what is TASK-X now?" by scanning every ref's history and taking the copy with the newest commit time (`git.historical_files`, `Repo._tasks_in_location` in `src/chitty/store.py`). Commit time is not causal order, so it picks wrong copies. The decided rule (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`) picks one authoritative copy without timestamps. This ticket builds that rule as a pure function only; `TASK-378` wires it into `Repo`.

Decisions:

- New module `src/chitty/ticket_source.py`. Create it first with the names below, the function raising `NotImplementedError`, so the tests fail on behaviour rather than at import.
- `WORKING_TREE` is a module constant meaning "read this checkout's file". Otherwise the result is the short name of a ref (`task-5`, `origin/task-5`, `main`) whose tip holds the ticket.
- `ticket_source(task_id: TaskId, provisional: bool, current_branch: str | None, main_branch: str, main_tip: str | None, local_tips: Mapping[str, str], remote_tips: Mapping[str, str], contains: Callable[[str, str], bool], changed_on_main: Callable[[str], bool]) -> str`. `main_tip` is `main_branch`'s commit, or `None` when it has none. `changed_on_main(ref)` is true when `main` changed this ticket's file since its merge base with `ref`. `local_tips` maps every visible local branch name to its commit; `remote_tips` maps every visible remote-tracking branch (`origin/task-5`) to its commit; `contains(a, b)` is true when commit `a` has `b` in its history, and `contains(c, c)` is true; callers pass Git ancestry, a partial order. The function does no Git, file or clock access.
- The ticket branch name is `str(task_id).lower()` (`TASK-5` gives `task-5`, `HUMAN-12` gives `human-12`). Candidates are the local branch with exactly that name and every remote-tracking branch whose name after its first `/` is exactly that name. Other names (`task-50`, local `feature/task-5`, `origin/x/task-5`) are not candidates. So a remote whose own name contains `/` never supplies a candidate: intended, as such remotes are rare.
- Rules, in order:
  1. `provisional` true: `WORKING_TREE`.
  2. No candidates: `main` is authoritative. `WORKING_TREE` when `current_branch == main_branch`, else `main_branch`.
  3. Otherwise, the chosen tip is the candidate commit that contains every other candidate commit. Among candidates at that commit, the local branch wins, else the remote-tracking candidate whose remote name (the part before its first `/`) sorts first. Result: `WORKING_TREE` when `current_branch` is the local candidate and its commit is the chosen one; else the chosen name.
     For example, `current_branch` is `task-5`, local `task-5` is at `A` and `origin/task-5` at a descendant `B`: the result is `origin/task-5`, not `WORKING_TREE`.
  4. No candidate contains all the others (diverged): raise `ChittyError` whose message contains each candidate's full short name (`origin/task-5`, not just `task-5`).
  5. Applied after rule 3 picks a tip: if `main_tip` is not `None` and `contains(main_tip, chosen tip)` (the branch equals `main` or is behind it: merged or stale), `main` is authoritative and rule 2's result applies instead. Otherwise, if `changed_on_main(chosen name)` is true (the ticket file changed on both sides), raise `ChittyError` naming the ticket, the chosen ref and `main`. Decided with the owner 2026-11-18: corner cases are errors for now, to see how often they happen. Deleting stale branches and rebasing in-flight ones are separate runner or clean-up actions, never part of a read.
- `current_branch` is `None` when `HEAD` is detached, including during a stopped rebase; the rules then never return `WORKING_TREE` except for a provisional ticket. Accepted: the ticket is read from its branch tip until the rebase finishes.
- A checkout knows only the branches it can see (a container may have only its own branch and `main`). The function treats its inputs as all there is.

Out of scope: any caller, reading files, and the write guard (`TASK-385`).

Tests: Hypothesis properties in a new `tests/test_property_ticket_source.py`. Generate commit graphs of two explicit shapes, so no property filters most inputs away: a chain (ancestry is index order) for rules 3 and 5 (with `main_tip` drawn from the chain, so it is sometimes ahead of, equal to or behind the candidates, or `None`), and a fork with at least two incomparable tips for rule 4, both with extra unrelated commits; `contains` is reachability including self; a task ID with a random prefix and number; local and remote branch maps drawn from candidate names, decoy names (as listed above) and unrelated names, pointing at random commits; `current_branch` drawn from candidate names, decoy names (including decoys used as `current_branch`, such as `feature/task-5`), `main_branch` and `None`; remote names without `/`; `provisional`; and `changed_on_main` as a generated set of refs for which it is true. Each property compares a returned value or asserts `ChittyError` specifically, so none can pass against the `NotImplementedError` stub.

## Acceptance Criteria

- [ ] Properties pass for rules 1 and 2: a provisional ticket gives `WORKING_TREE` whatever the other inputs; with no candidates the result is `WORKING_TREE` exactly when `current_branch == main_branch`, else `main_branch`
- [ ] Properties pass for rules 3 and 5: whenever one candidate commit contains all the others and is not contained by `main_tip`, the result is `WORKING_TREE` exactly when `current_branch` is the local candidate at that commit, otherwise it names a candidate at that commit, the local one when it is there, else the remote whose remote name sorts first; when `main_tip` contains that commit, the result is rule 2's; when `changed_on_main` is true for the chosen name and `main_tip` does not contain it, `ChittyError` names the ticket, that ref and `main`
- [ ] Properties pass for rule 4 and decoys: when no candidate contains all the others, `ChittyError` is raised and its message contains each candidate's full short name; adding or removing decoy and unrelated branches never changes the result
- [ ] Every property in `tests/test_property_ticket_source.py` fails against the `NotImplementedError` stub, and `make check` passes

## History

- 2026-11-18T16:20:02Z lively-quartz-crane → backlog
- 2026-11-18T16:21:15Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:21:15Z lively-quartz-crane backlog → planning
- 2026-11-18T16:21:24Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:23:03Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:23:03Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:23:14Z lively-quartz-crane planning → todo
- 2026-11-18T17:44:19Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:44:19Z lively-quartz-crane todo → planning
