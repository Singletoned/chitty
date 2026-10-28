---
title: Tests use a temporary inbox, never the real one
status: done
created: 2026-10-28
---

## Description

Test runs registered fresh, notes and repo in ~/.local/share/chitty/inbox/, pointing at deleted temp dirs, and a real suggestion was lost in inbox/repo/. Running init in a scratch clone did the same (circ). inbox_path already honours XDG_DATA_HOME, so the test base class should point it at a temp dir. These stale entries were deleted by hand on 2026-10-28. Pruning and warning about stale registrations is TASK-50.

## Acceptance Criteria

- [x] Every test runs with XDG_DATA_HOME set to a per-test temp dir (base class or equivalent, not per test)
- [x] A guard test fails if the suite creates or changes anything under the real inbox
- [x] AGENTS.md notes that tests isolate the inbox

## Plan

Inspect test environment setup and all test base classes, ensure XDG_DATA_HOME always points at each test temporary directory, add a guard that compares the real inbox before and after a suite operation, document the isolation rule in AGENTS.md, then run make check.

## Notes

Suggestion origin: circuitry

Needs refinement before implementation: make the required test inbox isolation outcome explicit, then decide whether stale-registration refusal and cleanup behavior belong here or in follow-up tickets. Add verifiable acceptance criteria for the chosen scope.

Reviewed: inspected inbox isolation and real-inbox guard in commit `d3a331e`; `make check` passes.

## Summary

Documented and retained per-test temporary XDG data homes through `RepoTestCase`, added a real-inbox snapshot guard around suggestion creation, and documented the inheritance requirement in AGENTS.md. Verified with `make check`.

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
- 2026-10-28 review → done
