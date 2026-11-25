---
title: Warn in `chitty check` on long tickets, bulky `todo` notes, and repeated cold reads
status: cold-read
created: 2026-11-25
provisional: true
---

## Description

Add three warning-level checks in `src/chitty/check.py` alongside `MAX_CRITERIA`, using module-level constants:

- `MAX_SPEC_WORDS = 500`: warn on `planning` or `todo` tickets when `Description` plus `Acceptance Criteria` word count (whitespace-split) exceeds `MAX_SPEC_WORDS`, suggesting simplifying or splitting.
- `MAX_TODO_NOTES_WORDS = 200`: warn on `todo` tickets when `Notes` word count exceeds `MAX_TODO_NOTES_WORDS`, suggesting clearing resolved notes with `--set-notes ''`.
- `MAX_COLD_READS = 2`: warn on `planning`, `cold-read`, or `todo` tickets when `task.transitions()` (`src/chitty/model.py`) has more than `MAX_COLD_READS` entries with `new == "cold-read"`, suggesting simplifying or splitting instead of another read.

Out of scope: changing `chitty check` exit codes, adding warnings to `chitty edit`, or changing how archived tickets are handled compared to `MAX_CRITERIA`.

## Acceptance Criteria

- [ ] In `src/chitty/check.py`, `check()` emits a `warning` `Problem` for each exceeded limit (`MAX_SPEC_WORDS`, `MAX_TODO_NOTES_WORDS`, `MAX_COLD_READS`) and none at or below the limit or outside the listed statuses, verified by Hypothesis property tests varying status, word counts, and transition histories.
- [ ] The new warnings are non-fatal (`chitty.check.errors(...)` excludes them), verified by tests passing `make check`.

## History

- 2026-11-25T18:17:32Z human → cold-read
