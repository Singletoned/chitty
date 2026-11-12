---
title: Specify property tests by default when planning, and look for missed ones in cold reads
status: cold-read
owner: human
created: 2026-11-12
---

## Description

- Workers test what criteria name, and criteria mostly test by example. In a random sample of 15 recent tickets, 11 could have had a property test and one did. TASK-289 said every Chitty error after the config loads is reported but tested only one error, so argument errors went unreported. TASK-266 said any prefix from every directory under `chitty/` but varied no criterion by branch, so directories that exist only on another branch failed three reviews.
- These guides reach every repository that uses Chitty, so the wording names no language or library.
- In `src/chitty/roles/plan.md`, replace the bullet beginning "Compare each decision in the description" with these three bullets, keeping its last sentence ("Say which test must fail ...") on the first:
  - "Specify property tests by default. Compare each decision in the description with the criteria, because workers test what criteria name. For each behaviour, write the property and what the test generates, for example "for any criteria list and valid N, only criterion N changes". If no property suits the ticket, give the reason in one line: a docs-only change, a small fixed set tested case by case, or behaviour that needs real external processes."
  - "These signal a property: structured input to structured output; inverse pairs (parse and format, export and import), which round-trip; a reference implementation (refactor, optimise, "same as", "replace X with Y"), which is the oracle; idempotence (re-run, retry, dedupe, normalise, "no-op if already"); independence of order or grouping (batching, pagination, merge, "in any order"); conservation (split, partition, "nothing lost"); claims over a class of inputs or data (all, every, each, any, always, never, except, unless, unique, sorted, at most, "no two"); open input domains (free text, Unicode, dates and time zones, paths, user files, nested data); parsers and validators ("never crashes on any input"); state machines and sequences of operations that keep an invariant; bounds and monotonicity; and a bug in an edge case, which shows the examples under-sampled the inputs."
  - "Where behaviour can be a pure function, from input values to output values with effects kept at its edges, have the ticket name that function and state its properties: it is far easier to test. A function the ticket names is part of its spec, so its tests may call it directly."
- In `src/chitty/roles/cold-read.md`, add a report bullet after "Surviving mutants": "Missed properties: behaviour tested only by example where a property fits, such as a round trip, a reference implementation, idempotence, order independence, conservation, a claim with all, every, never or except, an open input domain, a parser, or a state machine; and logic that could be a pure function but is not specified as one. Give each property and what to generate, or `none`. Say if a stated reason for having no property does not hold."
- `PLAN.md` "Pipeline and feedback": the "Spec tests exercise the public surface" paragraph also allows calling a pure function the ticket names, and says property tests are the default, with a stated reason when none suits.
- Out of scope: `src/chitty/roles/work.md` and `review.md`, and checking tickets mechanically for these words.

## Acceptance Criteria

- [ ] `chitty guide plan` prints the three new bullets and no longer prints the old "Compare each decision" bullet on its own; a test in `tests/test_guide_property_tests.py` asserts `Specify property tests by default`, `These signal a property` and `pure function`. It fails today.
- [ ] `chitty guide cold-read TASK-1` prints the `Missed properties` report bullet; a test in the same file asserts it. It fails today.
- [ ] No new text in `src/chitty/roles/` names a language or testing library: `grep -niE "python|hypothesis|pytest|unittest" src/chitty/roles/plan.md src/chitty/roles/cold-read.md` prints nothing.

## History

- 2026-11-12T18:38:04Z kind-yellow-vole → backlog
- 2026-11-12T19:53:21Z kind-yellow-vole: changed title, owner, description, acceptance criteria
- 2026-11-12T19:53:21Z kind-yellow-vole backlog → planning
- 2026-11-12T19:53:34Z kind-yellow-vole planning → cold-read
