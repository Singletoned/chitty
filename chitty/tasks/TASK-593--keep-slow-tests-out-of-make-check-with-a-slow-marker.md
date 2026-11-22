---
title: Keep slow tests out of `make check` with a `slow` marker
status: backlog
depends_on:
  - TASK-588
created: 2026-11-22
---

## Description

Planner, 2026-11-22: the person wants `make check` fast; any split is arbitrary, so start with a rough one and watch it with the timing history. First split: integration tests over about 3 s serially (for example `test_descendant_does_not_hold_call_open` 8.1 s, `test_run_cases` 7.9 s; serial run 842 s on 2026-11-22, `tmp/test-durations.log`). Open decision for the person before planning: landing runs `make check`, so slow tests would never run at landing; decide whether landing gets a deterministic full run (slow tests in, fixed examples) or relies on review having run `make test`.

## History

- 2026-11-22T17:16:36Z plucky-umber-wren → backlog
