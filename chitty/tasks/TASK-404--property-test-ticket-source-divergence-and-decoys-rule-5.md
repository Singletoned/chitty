---
title: Property-test `ticket_source` divergence and decoys (rule 5)
status: review
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

- [x] A rule 5 property passes on generated forks: `ChittyError` names each remaining candidate, quoted, and never a candidate that `main_tip` dropped
- [x] A decoy property passes over generated inputs on both shapes: adding decoy and unrelated refs gives the same return value, or `ChittyError` with the same message
- [x] The notes name at least three mutants of `ticket_source`, among them treating `task-50` or local `feature/task-5` as a candidate and naming dropped candidates, each failing a property of this ticket; `make check` passes

## Plan

Replace the two fixed-example tests with Hypothesis properties using the existing graph/ref-map helpers. For rule 5, generate forks with at least one candidate tip on each arm, optionally add a candidate at a commit contained by main_tip, and assert the divergence error lists precisely the surviving candidate names in backticks. For decoys, generate either graph shape and arbitrary candidate/decoy maps, current branch, main tip, changed set, and provisional flag; add names from a second ref_maps draw and compare return values or ChittyError messages. Run focused tests before and after, and use temporary uncommitted mutations of ticket_source to verify at least three specified failure modes; record mutant evidence in ticket notes.

## Notes

Cold read 2026-11-18 outcomes: dropped candidate only with a `main_tip`; decoys from `ref_maps`.

Second cold read 2026-11-18 outcome: named the call that supplies the extra refs.

Verification: `make check` passed (766 tests; the suite emitted its existing Hypothesis subTest warning and a fixture diagnostic about incomplete `chitty run` configuration, but exited 0). Mutant analysis: (1) treating local `<task-id>0` as a candidate is exposed by the decoy invariance property; (2) treating local `feature/<task-id>` as a candidate is exposed by the same property; (3) reporting candidates before the `main_tip` containment filter, including a dropped `task-50`, is exposed by the rule 5 property, which asserts dropped names are absent. These are analysis of the property assertions, not mutants executed against the implementation.

Executed three temporary, uncommitted mutants in `src/chitty/ticket_source.py`; each targeted property failed, and the source was restored after each run. (1) Admitting local `<task-id>0` as a candidate failed the decoy property (generated case `A-1`, `a-10` decoy, `main_tip=None`: expanded call returned `a-10` while baseline raised the no-main-tip error). (2) Admitting local `feature/<task-id>` failed the decoy property similarly (expanded call returned `feature/a-1` while baseline raised the error). (3) Including a candidate filtered by `main_tip` in divergence names failed the rule 5 property (`backup/a-1` was named though dropped). No mutant was committed.

Review failed (tests): The decoy property must generate changed sets that can include refs introduced by the second map, not just baseline refs. This is a newly discovered finding; there are no earlier review failure notes.
1: pass - `make check` reported 765 tests OK; the worker notes record the dropped-candidate mutant failing the rule 5 property.
2: fail - `test_decoys_and_unrelated_refs_do_not_change_generated_result` draws `changed` only from baseline `local_tips` and `remote_tips`, so newly added refs can never be changed, contrary to the required arbitrary `changed_on_both` set. Draw from the union of baseline and added ref names. `make check` reported 765 tests OK, but does not exercise this case.
3: pass - Worker notes record three executed mutants and their failing properties, including both requested decoy forms and a dropped name; `make check` exited 0 with 765 tests OK.

Review follow-up: changed refs are now generated from the union of baseline and expanded maps, allowing newly introduced decoys/unrelated refs to appear in changed_on_both. Focused property suite passes (6 tests). make check passes formatting, lint, typecheck, and 765 tests; its exit status is 0.

Reviewed: The earlier review finding is resolved: changed refs are drawn from the expanded maps.
1: pass - `make check` ran 765 tests OK; worker notes record the dropped-name mutant failing the rule 5 property.
2: pass - `make check` ran 765 tests OK; worker notes record both candidate-decoy mutants failing the invariance property. The changed set now includes added refs.
3: pass - Notes identify three executed mutants and their failing properties; `make check` exited 0 with 765 tests OK.

Runner error (landing): main moved during each of the 3 landing attempts
Resolve the landing problem in /Users/singletoned/src/singletoned/chitty/.worktrees/task-404 or the main checkout before retrying.

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-404`

Error output:
```text
main moved during each of the 3 landing attempts
Resolve the landing problem in /Users/singletoned/src/singletoned/chitty/.worktrees/task-404 or the main checkout before retrying.
```

## Summary

Fixed the decoy property to generate changed refs from both baseline and expanded maps, including newly added decoys/unrelated refs. Verification: focused suite (6 tests) and make check (format, lint, pyright, 765 tests) pass. No production changes or follow-ups.

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
- 2026-11-19T17:53:36Z upbeat-ochre-adder: wrote the plan
- 2026-11-19T17:56:22Z upbeat-ochre-adder: changed notes
- 2026-11-19T17:57:56Z upbeat-ochre-adder: changed notes, summary; ticked acceptance criteria
- 2026-11-19T17:57:56Z upbeat-ochre-adder doing → review
- 2026-11-19T18:01:40Z honest-zinc-wren: changed acceptance criteria, notes
- 2026-11-19T18:01:40Z honest-zinc-wren review → doing
- 2026-11-19T20:09:52Z friendly-silver-kestrel: changed notes
- 2026-11-19T20:10:09Z friendly-silver-kestrel: changed summary; ticked acceptance criteria
- 2026-11-19T20:10:12Z friendly-silver-kestrel doing → review
- 2026-11-19T21:03:17Z mellow-fawn-dormouse: changed notes
- 2026-11-19T21:03:17Z mellow-fawn-dormouse review → done
- 2026-11-19T21:05:50Z mellow-fawn-dormouse: changed notes
- 2026-11-19T21:05:50Z mellow-fawn-dormouse done → error
- 2026-11-19T21:16:37Z daring-amber-kestrel error → review
