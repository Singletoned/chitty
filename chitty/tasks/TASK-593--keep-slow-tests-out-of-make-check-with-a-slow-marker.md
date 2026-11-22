---
title: Keep slow tests out of `make check` with a `slow` marker
status: backlog
depends_on:
  - TASK-588
  - TASK-597
created: 2026-11-22
---

## Description

Planner, 2026-11-22: the person wants `make check` fast; any split is arbitrary, so start with a rough one and watch it with the timing history. First split: integration tests over about 3 s serially (for example `test_descendant_does_not_hold_call_open` 8.1 s, `test_run_cases` 7.9 s; serial run 842 s on 2026-11-22, `tmp/test-durations.log`).

Decided with the person, 2026-11-22: landing runs the full set of tests. Landing uses `check = "make check"` in `chitty.toml`, so once slow tests leave `make check` landing must run something that includes them. Planner's choice, to confirm while planning: fixed examples (profile `check`) with slow tests in, so landing is a repeatable regression gate and a newly drawn random example cannot block an unrelated ticket; random examples stay in `make test`, which work and review run. Keep the human-facing surface small: prefer an environment setting on the existing target over a new `Makefile` target. `chitty.toml` must not be edited on a ticket branch (`AGENTS.md`), so the landing command change is made in the main checkout after the ticket lands; say so in the ticket.

## History

- 2026-11-22T17:16:36Z plucky-umber-wren → backlog
- 2026-11-22T18:39:14Z plucky-umber-wren: changed description
- 2026-11-22T20:16:10Z plucky-umber-wren: changed dependencies
