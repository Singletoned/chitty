---
title: Tell work and review agents that every test failure is evidence of a bug
status: backlog
labels:
  - untestable
owner: untestable
created: 2026-11-22
---

## Description

Planner, 2026-11-22, the person's rule: every test failure is potential evidence of a bug in the code unless it is strongly shown to be an error in the test. Never rerun to get a pass. Work and review run the thorough tests (here `make test`) as well as the quick check. A failure in code the ticket did not touch: show it also fails on `main`, file a bug ticket with the failing input and output, note its ID, and carry on (the ticket can still pass). Guides reach every repository, so keep the wording general (`src/chitty/roles/work.md`, `review.md`); this repository's specifics go in `AGENTS.md`. Write after `TASK-587` to `TASK-589` land so the commands it names exist.

## History

- 2026-11-22T17:16:40Z plucky-umber-wren → backlog
