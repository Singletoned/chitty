---
title: Property-test `ticket_source` choosing among candidates (rules 4 and 6)
status: backlog
depends_on:
  - TASK-377
parent: TASK-376
created: 2026-11-18
---

## Description

`TASK-377` builds `ticket_source` in `src/chitty/ticket_source.py` and property-tests rules 1 to 3; the rules are in its description. This ticket replaces the fixed-example tests for rules 4 and 6 in `tests/test_property_ticket_source.py` with properties, reusing that file's `graphs()`, `task_ids()` and `ref_maps()` generators. Split from `TASK-377` on 2026-11-18, after two reviews rejected fixed examples. Change `src/chitty/ticket_source.py` only if a property finds a bug; then fix it and say so in the notes.

Build inputs whose answer is known by construction, rather than recomputing the rules in the test:

- Chain: draw `main_tip` as a commit index m, or `None`. Place one to four candidates (the local name and remote names) on commits above m, and optionally dropped candidates at or below m. The expected tip is the highest candidate commit above m; the expected name is the local candidate at that commit if there is one, else the remote whose remote name (before its first `/`) sorts first.
- Fork: put every remaining candidate on one arm, so they are comparable, and `main_tip` on the shared chain or the other arm, so it contains none of them. Expected as for the chain.
- Draw `current_branch` from the local candidate name, `main_branch`, a decoy and `None`. The result is `WORKING_TREE` exactly when `current_branch` is the local candidate name and the local candidate is at the expected tip; otherwise the expected name. Always include, in some examples, a remote candidate strictly ahead of a checked-out local one (the result is the remote name).
- Rule 6: the same inputs with `changed_on_both` true for the expected name, and for any other names drawn: `ChittyError` whose message contains the ticket ID, the expected ref and `main_branch`, each quoted in backticks. With `changed_on_both` true only for other names: the rule 4 result.

Each property asserts a returned value or `ChittyError` specifically. Tests match quoted names, so `task-5` is not found inside `origin/task-5`.

The code already exists, so evidence that the tests catch a wrong implementation comes from mutants run by hand and not committed: each changes `ticket_source` in one way, and the notes record which property failed.

## Acceptance Criteria

- [ ] Properties for rule 4 pass on both graph shapes: the result is `WORKING_TREE` exactly when `current_branch` is the local candidate name and the local candidate is at the expected tip, otherwise the candidate at the expected tip, the local one when it is there, else the remote whose remote name sorts first; generated examples include a remote strictly ahead of a checked-out local candidate
- [ ] Properties for rule 6 pass: with `changed_on_both` true for the expected name, `ChittyError` names the ticket, that ref and `main_branch`, each quoted; with it true only for other names, the result is the rule 4 result
- [ ] The notes name at least three mutants of `ticket_source`, among them remotes winning ties, the wrong remote order, and ignoring `changed_on_both`, each failing a property of this ticket; `make check` passes

## History

- 2026-11-18T21:31:03Z lively-quartz-crane → backlog
- 2026-11-18T21:31:17Z lively-quartz-crane: changed acceptance criteria
