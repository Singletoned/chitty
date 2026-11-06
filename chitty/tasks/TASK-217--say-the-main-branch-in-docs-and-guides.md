---
title: Say "the main branch" in docs and guides
status: backlog
priority: medium
depends_on:
  - TASK-216
created: 2026-11-06
---

## Description

After `TASK-216`, the integration branch is `main_branch` in `chitty.toml`. Wherever the guides and docs mean the integration branch, change "`main`" to "the main branch (`main_branch` in `chitty.toml`)", or plain "the main branch" once it has been introduced. Leave text that means the primary checkout ("main checkout") alone.

- `src/chitty/guide.md` and `src/chitty/roles/*.md`. These are the managed block, so bump `__version__` at patch level.
- `README.md`, around lines 34 and 125, and wherever else `grep -n '`main`' README.md` matches.
- `PLAN.md`, around lines 62, 134, 529, 650, 651, 716, 722 and 735, and the config section, which should document the optional `main_branch` setting (default `main`).

Don't run `chitty init` on the branch (`TASK-212`).

## Acceptance Criteria

- [ ] `grep -n '`main`' src/chitty/guide.md src/chitty/roles/*.md README.md PLAN.md` matches only text that means the primary checkout or quotes a command, and `PLAN.md`'s config section documents `main_branch`.
- [ ] `__version__` is bumped and `make check` passes.

## History

- 2026-11-06T16:48:08Z youthful-toad → backlog
- 2026-11-06T16:48:23Z youthful-toad: changed dependencies
- 2026-11-06T16:48:41Z youthful-toad: changed description
- 2026-11-06T16:49:20Z youthful-toad: changed description
