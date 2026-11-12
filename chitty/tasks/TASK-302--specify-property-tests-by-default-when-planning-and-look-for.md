---
title: Specify property tests by default when planning, and look for missed ones in cold reads
status: planning
owner: human
created: 2026-11-12
---

## Description

- Workers test what criteria name, and criteria mostly test by example. In a random sample of 15 recent tickets, 11 could have had a property test and one did. TASK-289 said every Chitty error after the config loads is reported but tested only one error, so argument errors went unreported. TASK-266 said any prefix from every directory under `chitty/` but varied no criterion by branch, so directories that exist only on another branch failed three reviews.
- These guides reach every repository that uses Chitty, so the wording names no language or library.
- In `src/chitty/roles/plan.md`, replace the bullet beginning `Compare each decision in the description` with the text in the block below, wrapped at about 80 columns like the rest of the file. The block is the exact Markdown to insert; add no quotation marks around it.

```markdown
- Specify property tests by default. Compare each decision in the description
  with the criteria, because workers test what criteria name. For each
  behaviour, write the property and what the test generates, for example "for
  any criteria list and valid N, only criterion N changes". If no property
  suits the ticket, give the reason in one line: a docs-only change, a small
  fixed set tested case by case, or behaviour that needs real external
  processes. Say which test must fail without the fix, because a nearby test
  may already pass.
- These signal a property:
  - structured input giving structured output;
  - a pair that undoes each other (parse and format, export and import): the
    round trip gives back the input;
  - an old implementation to match (refactor, optimise, "replace X with Y"):
    the new one gives the same results;
  - safe to repeat (retry, dedupe, normalise): doing it twice equals once;
  - order or grouping must not matter (batching, pages, merge);
  - nothing lost or made (split, partition, move): counts and totals match;
  - claims over a set of inputs: all, every, each, any, always, never, except,
    unless, unique, sorted, at most;
  - open inputs: free text, Unicode, dates and time zones, paths, user files,
    nested data;
  - parsers and validators: any input gives a result or a clear error, never
    a crash;
  - status changes and sequences of operations that must keep a rule;
  - limits: results stay in a range, or more input never gives less output;
  - a bug in an edge case (empty, zero, duplicate, boundary): the examples
    missed part of the inputs.
- Where behaviour can be a pure function, taking values and returning values
  with no file, network or clock access inside it, have the ticket name that
  function and state its properties: it is far easier to test. A function the
  ticket names is part of its spec, so its tests may call it directly.
```

- In `src/chitty/roles/cold-read.md`, add this report bullet after the `Surviving mutants` bullet, wrapped the same way:

```markdown
- Missed properties: behaviour tested only by example where a property fits
  (a round trip, matching an old implementation, safe to repeat, order not
  mattering, nothing lost, a claim with all, every, never or except, open
  inputs, a parser, or status changes), and logic that could be a pure function
  but is not specified as one. Give each property and what to generate, or
  `none`. Say if a stated reason for having no property does not hold.
```

- `PLAN.md` "Pipeline and feedback": the paragraph beginning `Spec tests exercise the public surface` also allows calling a pure function the ticket names, and says property tests are the default, with a stated reason when none suits.
- Out of scope: `src/chitty/roles/work.md` and `review.md`, and checking tickets mechanically for these words.

## Acceptance Criteria

- [ ] `chitty guide plan` prints the new bullets and no longer prints the old one: a test in `tests/test_guide_property_tests.py` asserts `Specify property tests by default`, `These signal a property`, `pure function` and `must fail without the fix` are present and `- Compare each decision` is absent. It fails today.
- [ ] `chitty guide cold-read TASK-1` prints the `Missed properties` report bullet; a test in the same file asserts it. It fails today.
- [ ] Guard, which passes before the change too: `grep -niE "python|hypothesis|pytest|unittest|quickcheck|fast-check|jest" src/chitty/roles/plan.md src/chitty/roles/cold-read.md` prints nothing.

## History

- 2026-11-12T18:38:04Z kind-yellow-vole → backlog
- 2026-11-12T19:53:21Z kind-yellow-vole: changed title, owner, description, acceptance criteria
- 2026-11-12T19:53:21Z kind-yellow-vole backlog → planning
- 2026-11-12T19:53:34Z kind-yellow-vole planning → cold-read
- 2026-11-12T19:56:03Z kind-yellow-vole: changed description, acceptance criteria
- 2026-11-12T19:56:03Z kind-yellow-vole cold-read → planning
