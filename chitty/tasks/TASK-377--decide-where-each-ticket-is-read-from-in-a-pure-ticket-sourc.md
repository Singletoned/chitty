---
title: Decide where each ticket is read from in a pure `ticket_source` function
status: todo
parent: TASK-376
created: 2026-11-18
---

## Description

Today Chitty answers "what is TASK-X now?" by scanning every ref's history and taking the copy with the newest commit time (`git.historical_files`, `Repo._tasks_in_location` in `src/chitty/store.py`). Commit time is not causal order, so it picks wrong copies. The decided rule (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`) picks one authoritative copy without timestamps. This ticket builds that rule as a pure function only; `TASK-378` wires it into `Repo` and computes its inputs.

Decisions:

- New module `src/chitty/ticket_source.py`. Before implementing, create it with the names below and the function raising `NotImplementedError`, run the new tests against that stub and record in the ticket's notes that every property fails; commit the stub only together with the implementation, so every commit passes `make check`.
- `WORKING_TREE = ""` is a module constant meaning "read this checkout's file" (the empty string is never a ref name). Otherwise the result is the short name of a ref (`task-5`, `origin/task-5`, `main`) whose tip holds the ticket.
- `ticket_source(task_id: TaskId, provisional: bool, current_branch: str | None, main_branch: str, main_tip: str | None, local_tips: Mapping[str, str], remote_tips: Mapping[str, str], contains: Callable[[str, str], bool], changed_on_both: Callable[[str], bool]) -> str`. The function does no Git, file or clock access.
  - `local_tips` maps every visible local branch name to its commit; `remote_tips` maps every visible remote-tracking branch (`origin/task-5`) to its commit (a key without `/` is ignored). `main_tip` is `main_branch`'s commit, or `None` when it has none; it is used for `main`, whatever `local_tips` says.
  - `contains(a, b)` is true when commit `a` has `b` in its history, and `contains(c, c)` is true; callers pass Git ancestry, a partial order. Nothing is contained by a `None` `main_tip`.
  - `changed_on_both(ref)` is true when this ticket's file changed both on `main` and on `ref` since their merge base. The caller (`TASK-378`) computes it against the same `main_tip`; the function only acts on it.
- The ticket branch name is `str(task_id).lower()` (`TASK-5` gives `task-5`, `HUMAN-12` gives `human-12`). Candidates are the local branch in `local_tips` with exactly that name and every remote-tracking branch whose name after its first `/` is exactly that name. Other names (`task-50`, `TASK-5`, local `feature/task-5`, `origin/x/task-5`) are not candidates; a remote whose own name contains `/` never supplies one (intended, as such remotes are rare). A `current_branch` that names a candidate not in `local_tips` (an unborn branch) is not a candidate.
- Rules, in order:
  1. `provisional` true: `WORKING_TREE`.
  2. Drop every candidate whose commit `main_tip` contains (merged or stale: the branch equals `main` or is behind it). Decided with the owner 2026-11-18; deleting such branches is a separate clean-up, never part of a read.
  3. No candidates left: `main` is authoritative. `WORKING_TREE` when `current_branch == main_branch`; else `main_branch`, unless `main_tip` is `None`, which raises `ChittyError` naming `main_branch` (a missing configured main branch is a configuration error).
  4. Otherwise, the chosen tip is the remaining candidate commit that contains every other remaining candidate. Among candidates at that commit, the local branch wins, else the remote-tracking candidate whose remote name (the part before its first `/`) sorts first. For example, `current_branch` is `task-5`, local `task-5` is at `A` and `origin/task-5` at a descendant `B`: the chosen name is `origin/task-5`.
  5. No remaining candidate contains all the others (diverged): raise `ChittyError` whose message contains each remaining candidate's full short name.
  6. If `changed_on_both(chosen name)`, raise `ChittyError` naming the ticket, the chosen ref and `main` (the ticket file changed on both sides). Otherwise the result is `WORKING_TREE` when `current_branch` is the local candidate and its commit is the chosen one, else the chosen name.
- Corner cases are errors for now, as the owner decided, to see how often they happen.
- `current_branch` is `None` when `HEAD` is detached, including during a stopped rebase; the rules then never return `WORKING_TREE` except for a provisional ticket. Accepted: the ticket is read from its branch tip until the rebase finishes.
- A checkout knows only the branches it can see (a container may have only its own branch and `main`). The function treats its inputs as all there is.

Out of scope: any caller, reading files, computing `changed_on_both`, and the write guard (`TASK-385`).

Tests: Hypothesis properties in a new `tests/test_property_ticket_source.py`. Generate commit graphs of two explicit shapes, so no property filters most inputs away: a chain (ancestry is index order) and a fork with at least two incomparable tips, both with extra unrelated commits; `contains` is reachability including self. Use both shapes for every rule. Draw `main_tip` from the graph (sometimes ahead of, equal to or behind each candidate, sometimes containing one fork tip but not the other) or `None`. Generate a task ID with a random prefix and number; local and remote branch maps drawn from candidate names, decoy names (as listed above, including the case variant) and unrelated names, pointing at random commits; `current_branch` drawn from candidate names, decoys, `main_branch`, `None`, and a candidate name absent from `local_tips`; remote names without `/`; `provisional`; and `changed_on_both` as a generated set of refs for which it is true. Each property compares a returned value or asserts `ChittyError` specifically. Every name in an error message is quoted in backticks, and tests match the quoted names, so `task-5` is not found inside `origin/task-5`; a dropped candidate is not named. Each rule's property builds inputs that reach its case (rule 5: always two incomparable remaining candidates; rule 6: `changed_on_both` always true for the chosen name), rather than relying on chance. Decoys with one `/` (`feature/task-5`) go only in `local_tips`; remote decoys are `origin/task-50` and `origin/x/task-5`. "Unchanged by decoys" means the same return value, or `ChittyError` with the same message.

## Acceptance Criteria

- [ ] Properties pass for rules 1 to 3: a provisional ticket gives `WORKING_TREE` whatever the other inputs; when every candidate is contained by `main_tip`, or there are none, the result is `WORKING_TREE` exactly when `current_branch == main_branch` (even when `main_tip` is `None`, an unborn `main`), else `main_branch`, or `ChittyError` naming `main_branch` when `main_tip` is `None`
- [ ] Properties pass for rules 4 and 6: whenever one remaining candidate commit contains all the others, the result is `WORKING_TREE` exactly when `current_branch` is the remaining local candidate at that commit, otherwise a candidate at that commit, the local one when it is there, else the remote whose remote name sorts first; and when `changed_on_both` is true for that name, `ChittyError` names the ticket, that ref and `main` instead
- [ ] Properties pass for rule 5 and decoys: when no remaining candidate contains all the others, `ChittyError` names each remaining candidate, including when `main_tip` contains a third, dropped one; adding or removing decoy and unrelated branches never changes the result
- [ ] The notes record every property failing against the `NotImplementedError` stub, and `make check` passes

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
- 2026-11-18T17:44:21Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:46:57Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:46:57Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:48:22Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:50:39Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:50:39Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:50:41Z lively-quartz-crane planning → todo
- 2026-11-18T17:53:59Z lively-quartz-crane: changed acceptance criteria
