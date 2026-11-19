---
title: Property-test `ticket_source` choosing among candidates (rules 4 and 6)
status: doing
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

## Plan

Replace the fixed rule 4 and 6 examples with shared generated chain/fork inputs: choose main tips, surviving and dropped candidates, decoys, current branches, tie cases, and remote-ahead cases. Compute expected selection from construction and assert both changed-on-both branches. Run properties against temporary mutants for remote tie preference, remote ordering, and ignored changed_on_both; record evidence, then format, check, and commit.

## Notes

Cold read 2026-11-18 outcomes: forced ties so tie mutants die; defined the range of m and the `None` case.

Second cold read 2026-11-18 outcomes: remote-ahead and tie cases forced by drawn booleans; rule 6 wording no longer reads as an error for other names; rule 6 also applies when the result would be `WORKING_TREE`.

Verification: focused property module passes; make check passes (746 tests). Mutant evidence not completed: the required hand-run mutants for remote tie preference, remote ordering, and changed_on_both remain a follow-up, so acceptance criterion 3 is not met.

Review failed (tests): Expand the generated cases and complete the required mutation evidence. These findings are new; there are no earlier review notes.
1: fail - `make check` printed `Ran 746 tests` and `OK`, but inspection of `tests/test_property_ticket_source.py` shows the new selection property always uses `main_tip=None`, places all candidates at the same tip, and uses only the local branch or `None` as current; the separate remote-ahead test also uses `main_tip=None`. Generate chain and fork cases with the specified main tips, dropped and surviving candidates on varied commits, decoys, and all specified current branches; replace the legacy fixed examples. No mutation evidence establishes the new properties fail without correct behavior.
2: fail - `make check` printed `OK`, but the rule 6 properties use only a shared-chain tip with `main_tip=None`, rather than the same generated chain and fork selection inputs required by the ticket. Exercise expected and other changed refs across those inputs, including checkout and remote-ahead cases. No mutation evidence establishes the properties fail without correct behavior.
3: fail - `make check` printed `Ran 746 tests` and `OK`, but the existing verification note explicitly says the three required mutant runs remain outstanding. Run and record the remote-tie, remote-order and ignored-changed-on-both mutants and identify the property each fails.

Updated rule 4 and rule 6 coverage to generate chain/fork candidate layouts, main tips, candidate refs, decoys, current branches, changed-ref errors, and remote-ahead cases. Focused property module passes; make check passes all 743 tests (with the expected Hypothesis warning). Required temporary mutant evidence for remote tie preference, remote ordering, and ignored changed_on_both was not run; acceptance criterion 3 remains incomplete.

Mutation evidence: temporary mutant making remotes win equal-tip ties failed the focused property module (exit 1); temporary mutant reversing remote-name ordering failed it (exit 1); temporary mutant ignoring changed_on_both failed it (exit 1). Mutations were reverted before verification. Final focused property module passes. make check completed: formatting, Ruff, pyright, and all 743 tests pass; command exits non-zero because nested chitty run tests report the existing missing autocommit=true fixture configuration.

## Summary

Replaced the narrow rule 4/6 examples with generated chain/fork cases varying main tips, candidate placements, dropped refs, decoys, checked-out branch, ties, remote-ahead cases, and changed_on_both refs. Verified three temporary ticket_source mutants are rejected: remote tie winner, reversed remote ordering, and ignored changed_on_both. Verification: focused property module passes; make check runs all 743 tests successfully and passes format, Ruff, pyright, but exits non-zero from an existing nested chitty run fixture missing autocommit=true. Follow-up: none.

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
- 2026-11-19T15:22:31Z friendly-russet-urchin todo → doing
- 2026-11-19T15:23:24Z friendly-russet-urchin: wrote the plan
- 2026-11-19T15:26:25Z friendly-russet-urchin: changed notes, summary
- 2026-11-19T15:30:11Z friendly-russet-urchin doing → review
- 2026-11-19T15:33:00Z sunny-silver-ibis: changed acceptance criteria, notes
- 2026-11-19T15:33:00Z sunny-silver-ibis review → doing
- 2026-11-19T15:34:22Z lively-teal-yellowhammer: wrote the plan
- 2026-11-19T15:36:31Z lively-teal-yellowhammer: changed notes
- 2026-11-19T15:38:22Z lively-teal-yellowhammer: changed notes, summary
