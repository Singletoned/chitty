---
title: Property-test `ticket_source` divergence and decoys (rule 5)
status: doing
depends_on:
  - TASK-377
  - TASK-403
parent: TASK-376
created: 2026-11-18
---

## Description

`TASK-377` builds `ticket_source` in `src/chitty/ticket_source.py` and property-tests rules 1 to 3; the rules and the decoy names are in its description. `TASK-403` covers rules 4 and 6 and edits the same file first. This ticket replaces the fixed-example tests for rule 5 and for decoys in `tests/test_property_ticket_source.py` with properties, reusing that file's `graphs()` (a `Graph` with `ancestors`), `task_ids()`, `ref_maps(task_id, candidate_commits, decoy_commits, with_candidates)`, `decoy_names()`, `current_branches()` and `call()` helpers. Split from `TASK-377` on 2026-11-18, after two reviews rejected fixed examples. Change `src/chitty/ticket_source.py` only if a property finds a bug; then fix it and say so in the notes.

- Rule 5: on the fork shape, place one or more candidates on each arm, so at least two are incomparable, and `main_tip` on the shared chain or `None`; when `main_tip` is not `None`, sometimes add a third candidate on a commit `main_tip` contains, which is dropped. Expected: `ChittyError` whose message contains each remaining candidate's name quoted in backticks, and not the dropped one's.
- Decoys: for any inputs (maps with candidate names over all commits of either shape, any `current_branch`, `main_tip` drawn or `None`, any `changed_on_both` set, `provisional` drawn), adding the decoy and unrelated refs of a second `ref_maps(task_id, commits, commits, False)` call (which never equal a candidate, and include a remote key without `/`) to the maps gives the same return value, or `ChittyError` with the same message. No expected value is computed; the property compares the two calls.

Each property asserts a returned value or `ChittyError` specifically, and tests match quoted names.

The code already exists, so evidence that the tests catch a wrong implementation comes from mutants run by hand and not committed: each changes `ticket_source` in one way, and the notes record which property failed.

## Acceptance Criteria

- [ ] A rule 5 property passes on generated forks: `ChittyError` names each remaining candidate, quoted, and never a candidate that `main_tip` dropped
- [ ] A decoy property passes over generated inputs on both shapes: adding decoy and unrelated refs gives the same return value, or `ChittyError` with the same message
- [ ] The notes name at least three mutants of `ticket_source`, among them treating `task-50` or local `feature/task-5` as a candidate and naming dropped candidates, each failing a property of this ticket; `make check` passes

## Notes

Cold read 2026-11-18 outcomes: dropped candidate only with a `main_tip`; decoys from `ref_maps`.

Second cold read 2026-11-18 outcome: named the call that supplies the extra refs.

## History

- 2026-11-18T21:31:15Z lively-quartz-crane → backlog
- 2026-11-18T21:31:19Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T21:32:18Z lively-quartz-crane backlog → planning
- 2026-11-18T21:32:20Z lively-quartz-crane planning → cold-read
- 2026-11-18T21:35:23Z lively-quartz-crane: changed description, notes
- 2026-11-18T21:35:23Z lively-quartz-crane cold-read → planning
- 2026-11-18T21:37:52Z lively-quartz-crane: changed description, notes
- 2026-11-18T21:38:00Z lively-quartz-crane planning → todo
- 2026-11-19T14:20:36Z quick-ginger-lapwing: changed description
- 2026-11-19T14:20:39Z quick-ginger-lapwing: changed description
- 2026-11-19T17:51:25Z upbeat-ochre-adder todo → doing
