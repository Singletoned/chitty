---
title: "Planning guide: do not ask for committed wrong-version tests for property tests"
status: backlog
created: 2026-11-23
---

## Description

The `chitty guide plan` text says that when tested code already exists, the worker should "commit each wrong version as a test" asserting the property fails on it. For Hypothesis property tests this clashes with normal practice: the runner finds failing inputs, and committed hand-written mutants add clutter and copied code that drifts. The real risk is a generator that never produces the cases a bug needs. In echonomicon on 2026-11-22, 5 of 11 planned wrong versions passed naive generators until the generators were biased toward boundaries. Suggest: for property tests, the planner validates the generators against listed wrong versions while planning, and the worker re-runs them once and records the result in a note. Or point at a mutation-testing tool such as `mutmut`. Keep committed wrong-version tests for example-based tests only. The project owner questioned the committed-mutant approach.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-23T10:24:10Z witty-russet-gannet → backlog
- 2026-11-23T10:24:11Z witty-russet-gannet: changed notes
