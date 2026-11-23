---
title: "Planning guide: check property-test generators against wrong versions instead of committing them"
status: doing
labels:
  - untestable
owner: friendly-zinc-dormouse
created: 2026-11-23
---

## Description

`src/chitty/roles/plan.md` (the bullet starting "When the code a ticket tests already exists", about line 29) tells planners to ask workers to commit each plausible wrong version of the code as a test asserting the test fails on it. For property tests this clashes with normal practice: committed hand-written mutants add clutter and copied code that drifts, and the real risk is a generator that never draws the inputs a bug needs. In echonomicon on 2026-11-22, 5 of 11 planned wrong versions passed naive generators until the generators were biased toward boundaries. The person agreed (2026-11-23) to change the guidance.

Change the bullet so that:

- For property tests, the planner runs the generators against each listed wrong version while planning and fixes any generator that lets one pass; the worker re-runs the property tests once against each wrong version and records the result in a note. Wrong versions are not committed.
- For example-based tests, keep today's advice: commit each wrong version as a test, or record a run in a note where that is impractical, saying why.

Keep the advice general (no Python or Hypothesis names): the guides reach every repository that uses Chitty. Update any test in `tests/` that pins the old wording, and `docs/plan/` if it repeats it.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-23T10:24:10Z witty-russet-gannet → backlog
- 2026-11-23T10:24:11Z witty-russet-gannet: changed notes
- 2026-11-23T10:29:52Z witty-russet-gannet: changed title, labels, owner, description
- 2026-11-23T10:29:52Z witty-russet-gannet backlog → todo
- 2026-11-23T12:01:31Z friendly-zinc-dormouse: changed owner
- 2026-11-23T12:01:31Z friendly-zinc-dormouse todo → doing
