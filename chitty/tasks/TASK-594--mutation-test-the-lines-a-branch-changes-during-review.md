---
title: Mutation-test the lines a branch changes during review
status: backlog
depends_on:
  - TASK-597
created: 2026-11-22
---

## Description

Planner, 2026-11-22, agreed with the person: a tool limited to the lines a branch changed, run in review or by `make test`; it can be dropped or moved to once a day if too slow. Open: mutmut 3 needs pytest and this repository uses `unittest`; cosmic-ray runs any test command. Check both before planning. Cold readers already write mutants by hand.

## Notes

Planner, 2026-11-22: after TASK-597 the suite runs under `pytest`, so `mutmut` is usable.

## History

- 2026-11-22T17:16:38Z plucky-umber-wren → backlog
- 2026-11-22T20:16:12Z plucky-umber-wren: changed dependencies
- 2026-11-22T20:16:17Z plucky-umber-wren: changed notes
