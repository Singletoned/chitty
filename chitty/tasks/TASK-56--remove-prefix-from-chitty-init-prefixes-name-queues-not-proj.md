---
title: Remove --prefix from chitty init; prefixes name queues, not projects
status: todo
created: 2026-10-28
---

## Description

chitty init --prefix lets a repo rename its default context's prefix to the project name (e.g. CIRCUIT-68). That adds nothing, since a ticket's project is the repo it lives in, and it caused TASK-43. Prefixes should name queues (TASK for tasks/, HUMAN for human/), not projects or types. Type belongs in labels: an ID must never change, but a ticket's type does (a suggestion is refined into a task; a bug turns out to be a feature). New repos always get TASK. Existing repos keep their configured prefix, because renumbering would break Task: lines in commits and outside references.

## Acceptance Criteria

- [ ] chitty init has no --prefix option; a new repo's default context uses TASK
- [ ] Existing chitty.toml files with a custom contexts.*.prefix still load and work unchanged, and init leaves them alone
- [ ] Adding further contexts with their own prefix in config still works
- [ ] PLAN.md states the rule (prefixes name queues, not projects or types; type is a label) and the CLI section, README and tests drop --prefix

## Notes

Decided with the human. Type-in-ID (bug-01, suggestion-02) was considered and rejected because IDs must be stable; use labels and chitty list filtering instead.

## History

- 2026-10-28 → todo
