---
title: Guide agents through setting up chitty run
status: todo
priority: medium
parent: TASK-106
created: 2026-11-09
---

## Description

Add a focused `chitty guide setup` page for a coding agent helping a person enable `chitty run`. Explain how to initialize from the main checkout and edit the existing repository-root `chitty.toml`, or `[tool.chitty]` in the root `pyproject.toml` when that is the chosen config; never create both. Cover `autocommit`, `setup`, `check`, and a default `agent_command` or a `[agent_commands]` entry chosen with `chitty run --agent NAME`. Each selected command needs both `{mode}` and `{id}`, or `{prompt}`. Explain agent integration and deliberately trying a real ticket. Keep it useful for new and existing repositories; do not modify configuration automatically or add a wizard.

## Acceptance Criteria

- [ ] `chitty guide setup` works outside a repository, names the prerequisites and exact config location, and explains main-checkout versus ticket-worktree changes and how to verify the setup.
- [ ] Dedicated guide tests fail before implementation and pass afterward; `README.md` and `PLAN.md` document the new guide; `make check` passes.

## Notes

Read-only cold read clarified that there are two mutually exclusive config locations and that named agent commands still require placeholders; both are included in the description.

## History

- 2026-11-09T11:51:54Z eager-puffin → todo
- 2026-11-09T11:53:11Z eager-puffin: changed description, notes
