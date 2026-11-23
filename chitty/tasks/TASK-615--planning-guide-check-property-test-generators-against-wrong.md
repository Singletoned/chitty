---
title: "Planning guide: check property-test generators against wrong versions instead of committing them"
status: review
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

## Summary

Rewrote the wrong-versions bullet in `src/chitty/roles/plan.md`. Example-based tests: commit each wrong version as a test, or record a run in a note where that is impractical, saying why. Property tests: the planner runs the generators against each wrong version while planning and fixes any that let one pass; the worker re-runs them once against each and notes the result; the wrong versions are not committed. The text is compressed to fit the 1340-word budget for `plan.md` (now 1324).

`docs/plan/pipeline-and-feedback.md` records the exception and the echonomicon evidence. `tests/test_guide_planner_evidence.py` gains `test_property_test_wrong_versions_are_run_not_committed`. It failed against the unchanged `plan.md` (checked by stashing only that file); the existing assertions still pass.

Verification: `make check` passed (1171 tests).

## History

- 2026-11-23T10:24:10Z witty-russet-gannet → backlog
- 2026-11-23T10:24:11Z witty-russet-gannet: changed notes
- 2026-11-23T10:29:52Z witty-russet-gannet: changed title, labels, owner, description
- 2026-11-23T10:29:52Z witty-russet-gannet backlog → todo
- 2026-11-23T12:01:31Z friendly-zinc-dormouse: changed owner
- 2026-11-23T12:01:31Z friendly-zinc-dormouse todo → doing
- 2026-11-23T12:21:03Z friendly-zinc-dormouse: changed summary
- 2026-11-23T12:21:03Z friendly-zinc-dormouse doing → review
