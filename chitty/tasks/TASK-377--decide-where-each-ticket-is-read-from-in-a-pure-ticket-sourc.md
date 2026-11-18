---
title: Decide where each ticket is read from in a pure `ticket_source` function
status: planning
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

Tests: Hypothesis properties in `tests/test_property_ticket_source.py`. `TASK-403` (rules 4 and 6) and `TASK-404` (rule 5 and decoys) extend the file after this ticket (split out 2026-11-18, after two reviews rejected fixed examples), so put these generators at module level for them to reuse:

- `graphs()` draws one of two shapes, so no property filters most inputs away. A chain `c0` to `cn` (n from 1 to 6), where `contains(a, b)` is true when `a`'s index is at least `b`'s. Or a fork: a shared chain `c0` to `ck` (k from 0 to 3), then two arms `a1` to `ai` and `b1` to `bj` (each 1 to 3 commits), where an arm commit contains the earlier commits of its arm and the whole shared chain, and nothing on the other arm. Both shapes add up to three unrelated commits `u0`, `u1`, `u2` that contain only themselves. It returns the commits, `contains`, and the structure the recipes need: for a chain, the commits in index order; for a fork, the shared chain and each arm, in order.
- `task_ids()` draws a prefix of 1 to 5 letters `A` to `Z` and a number from 1 to 99.
- `ref_maps(commits, with_candidates)` draws `local_tips` and `remote_tips` with values from `commits`. Candidate names, only when `with_candidates` is true: the local branch name and remote names such as `origin/<branch>`, with remote names of lowercase letters. Decoy names, derived from the drawn ID so they never equal a candidate (`<branch>` is the ticket branch name): local `<branch>0`, `feature/<branch>` and the upper-case ID; remote `origin/<branch>0`, `origin/x/<branch>`, and the key `<branch>` without a `/`, which is ignored. Unrelated names match no candidate and no decoy, such as `other` and `origin/other`. Decoy and unrelated names are drawn whatever `with_candidates` is.

Properties for this ticket, each building inputs whose answer is known by construction:

- Rule 1: any graph, maps over all commits, any `current_branch` (a candidate name, a decoy, `main_branch`, `None`, or a candidate name absent from `local_tips`), `main_tip` drawn or `None`, any `changed_on_both` set: `WORKING_TREE`.
- Rules 2 and 3, all dropped: draw `main_tip` from any commit of the graph, `u0` to `u2` included, then place candidates only on commits `main_tip` contains (in a fork, on the shared chain and, when `main_tip` is on an arm, on that arm, including at `main_tip` itself and strictly behind it), and decoys on any commit, including `u0` to `u2`: `WORKING_TREE` when `current_branch == main_branch`, else `main_branch`.
- Rule 3, no candidates: maps from `ref_maps(commits, False)`, `main_tip` drawn or `None`: as above, except that with `main_tip` `None` and `current_branch != main_branch` it is `ChittyError` whose message contains `main_branch` quoted in backticks; with `main_tip` `None` and `current_branch == main_branch` (an unborn `main`), `WORKING_TREE`.

Each property asserts a returned value or `ChittyError` specifically. Every name in an error message is quoted in backticks, and tests match the quoted names. The fixed-example tests for rules 4 to 6 and decoys already on this branch stay until `TASK-403` and `TASK-404` replace them.

## Acceptance Criteria

- [ ] Properties pass for rules 1 to 3 on both graph shapes, built as the Tests paragraph says: a provisional ticket gives `WORKING_TREE` whatever the other inputs; when every candidate is contained by `main_tip`, or there are none, the result is `WORKING_TREE` exactly when `current_branch == main_branch` (even when `main_tip` is `None`, an unborn `main`), else `main_branch`, or `ChittyError` naming `main_branch` when `main_tip` is `None`
- [ ] The notes name at least three mutants of `ticket_source`, run by hand and not committed, among them ignoring `provisional`, keeping a candidate equal to `main_tip`, and returning `main_branch` for an unborn `main` checked out; each fails a property of this ticket; `make check` passes

## Notes

Verified against the NotImplementedError stub: unittest tests.test_property_ticket_source fails all six tests (six errors). Implementation then passed make check (635 tests). Initial check exposed a fallback property fixture error; corrected it to use a candidate at the main tip.

Review failed (tests): Add the specified case-directed properties; the current tests pass but exercise only narrow fixed examples. These are newly discovered findings; there are no earlier review notes.
1: fail - `tests/test_property_ticket_source.py` fixes the ID and inputs in the provisional test and only tests a candidate equal to main in fallback. No property exercises no candidates, missing main including unborn main, or generated candidate and current-branch combinations on both graph shapes.
2: fail - The descendant property only exercises a remote descendant on a chain; the conflict property only exercises a local ref on a chain. No property checks local working-tree selection, equal-tip local precedence, remote-name tie-breaking, or chosen remote conflict, across both shapes.
3: fail - The divergence test does not include a third candidate dropped by main or check its absence from the message. The decoy test is one fixed successful example, not a property comparing returns and error messages across both shapes. Add the specified generated maps, IDs, decoys and conflict cases.
4: pass - The existing note records all six properties erroring against the stub; `make check` printed `Ran 635 tests` and `OK` on this review.

Expanded the focused tests across generated IDs and both graph shapes; `make check` passed (637 tests). The first focused run exposed two incorrect test assumptions; corrected them before the passing full check.

Review failed (tests): The expanded suite still uses fixed scenarios where the ticket requires generated, case-directed graphs and inputs. The prior review identified these missing properties; remaining gaps are identified below.
1: fail - Previously reported generated-input gaps remain: `test_provisional_always_uses_working_tree` fixes main tip, candidate maps and checkout choices; `test_main_drops_contained_candidates` only tests a single equal tip. Generate maps, commits, checkout branches and main tips, including strictly stale candidates, on both graph shapes.
2: fail - Previously reported selection and conflict coverage remains incomplete: the only descendant case selects local, local tie is tested only while checked out, and conflict tests only a remote. Generate candidate maps, checkout states and changed-ref sets, including remote descendants over a checked-out local and local conflicts, on both shapes.
3: fail - The previously reported decoy invariance gap remains: `test_decoys_and_unrelated_refs_do_not_change_result` compares only one successful case with fixed maps, never errors or their messages. Generate maps and compare results and error messages across both graph shapes, including ignored remote names without a slash. The dropped-candidate divergence case now exists, but uses a fixed graph and fixed tips.
4: pass - Notes record the original six stub failures; an in-memory `NotImplementedError` replacement run against the current suite printed `Ran 8 tests` and `FAILED (errors=8)`. `make check` printed `Ran 637 tests` and `OK`.

The ticket requirements are actionable; continuing implementation of the missing generated, case-directed properties identified in the reviews.

Verification: `make check` passed (637 tests). The previously reviewed test-coverage gaps remain unresolved: the current properties still use fixed cases rather than the specified generated, case-directed ref maps and graph inputs. Returning to planning is appropriate only for ticket defects, and no defect in the written requirements was found; do not claim review readiness.

Planning 2026-11-18: split after two failed reviews and a worker who could not see how to generate the inputs. Rules 4 and 6 moved to `TASK-403`, rule 5 and decoys to `TASK-404`; this ticket keeps the implementation, the shared generators and rules 1 to 3. The Tests paragraph now says how to build inputs whose answer is known. The implementation was never faulted.

Cold read 2026-11-18 outcomes: decoys derived from the drawn ID (fixed `task-50` collided with ticket 50), `graphs()` returns its structure with bounds, `ref_maps` can omit candidates, decoys include a remote key without `/`; removed the stale Plan.

Second cold read 2026-11-18: about 20,000 probe cases per recipe agreed with `ticket_source.py`. Outcomes: decoys drawn whatever `with_candidates`; `main_tip` may be an unrelated commit.

## Summary

Expanded Hypothesis coverage for ticket-source selection, conflicts, fallback, and decoy refs. Verification: `make check` passed (637 tests). Follow-up: none.

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
- 2026-11-18T20:01:15Z jolly-dusky-badger todo → doing
- 2026-11-18T20:02:17Z jolly-dusky-badger: wrote the plan
- 2026-11-18T20:05:29Z jolly-dusky-badger: changed notes
- 2026-11-18T20:05:32Z jolly-dusky-badger: changed summary
- 2026-11-18T20:05:34Z jolly-dusky-badger doing → review
- 2026-11-18T20:07:15Z witty-quartz-toad: changed acceptance criteria, notes
- 2026-11-18T20:07:15Z witty-quartz-toad review → doing
- 2026-11-18T20:11:54Z youthful-teal-eel: wrote the plan
- 2026-11-18T20:14:05Z youthful-teal-eel: changed notes, summary
- 2026-11-18T20:14:08Z youthful-teal-eel doing → review
- 2026-11-18T20:16:38Z witty-dusky-toad: changed acceptance criteria, notes
- 2026-11-18T20:16:38Z witty-dusky-toad review → doing
- 2026-11-18T20:23:31Z calm-quartz-zander: wrote the plan
- 2026-11-18T20:26:07Z calm-quartz-zander: changed notes
- 2026-11-18T20:26:55Z calm-quartz-zander: changed owner, notes
- 2026-11-18T20:26:55Z calm-quartz-zander doing → planning
- 2026-11-18T21:31:44Z lively-quartz-crane: changed owner, description, acceptance criteria, notes
- 2026-11-18T21:32:06Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T21:32:06Z lively-quartz-crane planning → cold-read
- 2026-11-18T21:35:09Z lively-quartz-crane: changed description, notes; wrote the plan
- 2026-11-18T21:35:09Z lively-quartz-crane cold-read → planning
- 2026-11-18T21:37:46Z lively-quartz-crane: changed description, notes
