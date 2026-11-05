---
title: Point the `AGENTS.md` block at `chitty guide plan`
status: backlog
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

The block `chitty init` writes into a repository's `AGENTS.md` comes from `src/chitty/guide.md`. It never mentions `chitty guide plan` or cold reads, so an agent writing tickets in another repository only learns that "Backlog tasks need refinement". `src/chitty/roles/plan.md` has the advice, but nothing leads there. `TASK-143` rewrites the whole block and will add such a pointer, but it waits on `TASK-142` and `TASK-144`; this is the one line, sooner.

Directly after the `Backlog tasks need refinement` bullet in `guide.md`, add: "- Writing or refining tickets? Run `chitty guide plan` first: it says how to write them and cold-read them." Then run `chitty init` and commit `AGENTS.md` and `chitty.toml`, because `guide.md` reaches `AGENTS.md` only that way. `TASK-143` must keep the pointer, which it already plans to.

## Acceptance Criteria

- [ ] A test in `TestGuide` in `tests/test_cli.py` shows `guide()` containing `chitty guide plan`
- [ ] `__version__` is bumped above `main`'s, and `AGENTS.md`'s managed block equals `chitty guide`

## History

- 2026-11-05T14:13:55Z mellow-newt → backlog
