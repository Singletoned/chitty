---
title: Warn in `chitty check` on long tickets, bulky `todo` notes, and repeated cold reads
status: review
created: 2026-11-25
moved_from: TASK-WQSEDK
---

## Description

Add three warning-level checks in `src/chitty/check.py` alongside `MAX_CRITERIA`, using module-level constants:

- `MAX_SPEC_WORDS = 500`: warn on `planning` or `todo` tickets when whitespace-split words in `task.section("Description")` plus `criterion.text` across `task.criteria` exceed `MAX_SPEC_WORDS`, suggesting simplifying or splitting.
- `MAX_TODO_NOTES_WORDS = 200`: warn on `todo` tickets when whitespace-split words in `task.section("Notes")` exceed `MAX_TODO_NOTES_WORDS`, suggesting clearing resolved notes with `--set-notes ''`.
- `MAX_COLD_READS = 2`: warn on `planning`, `cold-read`, or `todo` tickets when `task.transitions()` (`src/chitty/model.py`) has more than `MAX_COLD_READS` entries with `new == "cold-read"`, suggesting simplifying or splitting instead of another read.

Out of scope: changing `chitty check` exit codes, adding warnings to `chitty edit`, or changing how archived tickets are handled compared to `MAX_CRITERIA`.

## Acceptance Criteria

- [x] In `src/chitty/check.py`, `check()` emits a `warning` `Problem` (excluded by `errors()`) for each exceeded limit (`MAX_SPEC_WORDS`, `MAX_TODO_NOTES_WORDS`, `MAX_COLD_READS`) and none at or below the limit or outside the listed statuses, verified by Hypothesis property tests varying status, word counts, and transition histories.

## Plan

Add the three status-scoped warning checks alongside the existing criteria warning. Exercise boundaries, statuses, combined specification word counts and transition histories through property tests of check(), including warning severity and errors() filtering.

## Notes

Property test confirmed failing against the original checker: planning ticket with 499 description words and 2 criterion words produced no specification warning.

## Summary

Added status-scoped warnings for specification length, todo notes and repeated cold reads, with property tests covering boundaries, histories and archived tickets. make check passed.

## History

- 2026-11-25T18:17:32Z human → cold-read
- 2026-11-25T18:19:10Z human: changed description, acceptance criteria
- 2026-11-25T18:19:10Z human cold-read → todo
- 2026-11-25T18:32:36Z human: renumbered from TASK-WQSEDK
- 2026-11-25T20:54:43Z golden-maroon-urchin todo → doing
- 2026-11-25T20:58:41Z golden-maroon-urchin: wrote the plan
- 2026-11-25T21:02:01Z golden-maroon-urchin: changed notes
- 2026-11-25T21:06:21Z golden-maroon-urchin: changed summary; ticked acceptance criteria
- 2026-11-25T21:08:55Z golden-maroon-urchin doing → review
