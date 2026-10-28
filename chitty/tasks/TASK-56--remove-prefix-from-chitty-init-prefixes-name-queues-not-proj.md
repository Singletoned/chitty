---
title: Remove --prefix from chitty init; prefixes name queues, not projects
status: review
created: 2026-10-28
---

## Description

chitty init --prefix lets a repo rename its default context's prefix to the project name (e.g. CIRCUIT-68). That adds nothing, since a ticket's project is the repo it lives in, and it caused TASK-43. Prefixes should name queues (TASK for tasks/, HUMAN for human/), not projects or types. Type belongs in labels: an ID must never change, but a ticket's type does (a suggestion is refined into a task; a bug turns out to be a feature). New repos always get TASK. Existing repos keep their configured prefix, because renumbering would break Task: lines in commits and outside references.

## Acceptance Criteria

- [x] chitty init has no --prefix option; a new repo's default context uses TASK
- [x] Existing chitty.toml files with a custom contexts.*.prefix still load and work unchanged, and init leaves them alone
- [x] Adding further contexts with their own prefix in config still works
- [x] PLAN.md states the rule (prefixes name queues, not projects or types; type is a label) and the CLI section, README and tests drop --prefix

## Plan

Remove `--prefix` from the `init` command and its implementation while retaining configured context prefixes. Update CLI, tests and documentation to establish `TASK` for a new repository and custom prefixes only through configuration. Run `make check`, then hand off for independent review.

## Notes

Decided with the human. Type-in-ID (bug-01, suggestion-02) was considered and rejected because IDs must be stable; use labels and chitty list filtering instead.

## Summary

Removed `chitty init --prefix`; new repositories always configure `TASK`. Existing custom default and additional context prefixes remain configuration-driven and are covered by tests. Verified with `make check`.

## History

- 2026-10-28 → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
