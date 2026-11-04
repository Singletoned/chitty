---
title: Fail `make check` when a setup change has no version bump
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

Accepted by the human from the `TASK-108` retro, proposal 1. A missed or lost `__version__` bump caused failures on `TASK-93`, `TASK-104` and `TASK-126`, and two tickets bumping to the same version merge silently, so repositories never learn about the later change.

Add a check that `make check` runs: if `src/chitty/guide.md`, `src/chitty/integrations/pi/chitty.ts`, or the `INITIAL_CONFIG` template in `src/chitty/config.py` differs from `main`'s, `__version__` must be above `main`'s, compared numerically. Compare the template's text rather than the whole of `config.py`, which changes for other reasons. It needs only Git and the standard library, and fails with a message naming the changed files and both versions. Add `src/chitty/roles/` to the list if it exists by then.

On `main` itself, there is nothing to compare, so it passes.

## Acceptance Criteria

- [ ] Tests in a temporary Git repository show each listed change failing without a higher version, passing with one, a matching version failing, an unrelated `config.py` change passing, and running on `main` passing
- [ ] `make check` runs it, and it passes in the release workflow's checkout

## History

- 2026-11-04T20:45:25Z mellow-newt → backlog
