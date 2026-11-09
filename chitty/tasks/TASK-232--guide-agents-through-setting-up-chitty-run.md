---
title: Guide agents through setting up chitty run
status: doing
priority: medium
parent: TASK-106
created: 2026-11-09
---

## Description

Add a focused `chitty guide setup` page for a coding agent helping a person enable `chitty run`. Explain how to initialize from the main checkout and edit the existing repository-root `chitty.toml`, or `[tool.chitty]` in the root `pyproject.toml` when that is the chosen config; never create both. Cover `autocommit`, `setup`, `check`, and a default `agent_command` or a `[agent_commands]` entry chosen with `chitty run --agent NAME`. Each selected command needs both `{mode}` and `{id}`, or `{prompt}`. Explain agent integration and deliberately trying a real ticket. Improve `chitty guide --help` so it lists the available guides and concrete usage examples, including the general `chitty guide` and new setup guide. Keep this useful for new and existing repositories; do not modify configuration automatically or add a wizard.

## Acceptance Criteria

- [ ] `chitty guide setup` works outside a repository, names the prerequisites and exact config location, and explains main-checkout versus ticket-worktree changes and how to verify the setup. `chitty guide --help` identifies available guides and shows commands for general, setup and ticket-specific guidance.
- [ ] Dedicated guide tests fail before implementation and pass afterward; `README.md` and `PLAN.md` document the new guide; `make check` passes.

## Plan

Add a packaged setup role, expose it in role dispatch without allowing ticket IDs, and improve the existing guide command help. Add fail-first dedicated CLI tests for the setup page and help examples. Link the page from README and document the role in PLAN. Run make format and make check, inspect tool changes, commit implementation, then hand off for review.

## Notes

Read-only cold read clarified that there are two mutually exclusive config locations and that named agent commands still require placeholders; both are included in the description.

## History

- 2026-11-09T11:51:54Z eager-puffin → todo
- 2026-11-09T11:53:11Z eager-puffin: changed description, notes
- 2026-11-09T11:53:37Z eager-puffin: changed description, acceptance criteria; wrote the plan
- 2026-11-09T11:53:37Z eager-puffin todo → doing
