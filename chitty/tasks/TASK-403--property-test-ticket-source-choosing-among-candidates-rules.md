---
title: Property-test `ticket_source` choosing among candidates (rules 4 and 6)
status: todo
depends_on:
  - TASK-377
parent: TASK-376
created: 2026-11-18
---

## Description

`TASK-377` builds `ticket_source` in `src/chitty/ticket_source.py` and property-tests rules 1 to 3; the rules are in its description. This ticket replaces the fixed-example tests for rules 4 and 6 in `tests/test_property_ticket_source.py` with properties, reusing that file's `graphs()` (a `Graph` with `ancestors`), `task_ids()`, `ref_maps(task_id, candidate_commits, decoy_commits, with_candidates)`, `decoy_names()`, `current_branches()` and `call()` helpers. Split from `TASK-377` on 2026-11-18, after two reviews rejected fixed examples. Change `src/chitty/ticket_source.py` only if a property finds a bug; then fix it and say so in the notes.

Build inputs whose answer is known by construction, rather than recomputing the rules in the test:

- Chain: draw `main_tip` as a commit index m from 0 to n-1, so a commit lies above it, or `None`, when candidates go on any commit. Place one to four candidates (the local name and remote names) on commits above m, and optionally dropped candidates at or below m. The expected tip is the highest candidate commit above m; the expected name is the local candidate at that commit if there is one, else the remote whose remote name (before its first `/`) sorts first.
- Fork: put every remaining candidate on one arm, so they are comparable, and `main_tip` on the shared chain or on the other arm, so it contains none of them. Expected as for the chain.
- Draw `current_branch` from the local candidate name, `main_branch`, a decoy and `None`. The result is `WORKING_TREE` exactly when `current_branch` is the local candidate name and the local candidate is at the expected tip; otherwise the expected name. Draw a boolean that, when true, builds a remote candidate strictly ahead of a checked-out local one (the result is the remote name).
- Ties: draw a boolean that, when true, puts the local candidate, or two or more remotes, on the expected tip, so that tie-breaking is exercised.
- Rule 6: the same inputs with `changed_on_both` true for the expected name (other names may also be true), also when the rule 4 result would be `WORKING_TREE`: `ChittyError` whose message contains the ticket ID, the expected ref and `main_branch`, each quoted in backticks. With `changed_on_both` true only for other names: the rule 4 result.

Each property asserts a returned value or `ChittyError` specifically. Tests match quoted names, so `task-5` is not found inside `origin/task-5`.

The code already exists, so evidence that the tests catch a wrong implementation comes from mutants run by hand and not committed: each changes `ticket_source` in one way, and the notes record which property failed.

## Acceptance Criteria

- [ ] Properties for rule 4 pass on both graph shapes: the result is `WORKING_TREE` exactly when `current_branch` is the local candidate name and the local candidate is at the expected tip, otherwise the candidate at the expected tip, the local one when it is there, else the remote whose remote name sorts first; generated examples include a remote strictly ahead of a checked-out local candidate
- [ ] Properties for rule 6 pass: with `changed_on_both` true for the expected name, `ChittyError` names the ticket, that ref and `main_branch`, each quoted; with it true only for other names, the result is the rule 4 result
- [ ] The notes name at least three mutants of `ticket_source`, among them remotes winning ties, the wrong remote order, and ignoring `changed_on_both`, each failing a property of this ticket; `make check` passes

## Notes

Cold read 2026-11-18 outcomes: forced ties so tie mutants die; defined the range of m and the `None` case.

Second cold read 2026-11-18 outcomes: remote-ahead and tie cases forced by drawn booleans; rule 6 wording no longer reads as an error for other names; rule 6 also applies when the result would be `WORKING_TREE`.

## History

- 2026-11-18T21:31:03Z lively-quartz-crane → backlog
- 2026-11-18T21:31:17Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T21:32:12Z lively-quartz-crane backlog → planning
- 2026-11-18T21:32:16Z lively-quartz-crane planning → cold-read
- 2026-11-18T21:35:18Z lively-quartz-crane: changed description, notes
- 2026-11-18T21:35:18Z lively-quartz-crane cold-read → planning
- 2026-11-18T21:37:49Z lively-quartz-crane: changed description, notes
- 2026-11-18T21:37:56Z lively-quartz-crane planning → todo
- 2026-11-19T14:20:34Z quick-ginger-lapwing: changed description
