---
title: Guide agents through setting up chitty run
status: todo
priority: medium
parent: TASK-106
created: 2026-11-09
---

## Description

Add a focused `chitty guide setup` page for a coding agent helping a person enable `chitty run`. Explain how to initialize from the main checkout, configure `autocommit`, `setup`, `check`, and an agent command with role/ticket placeholders (or a named agent command), install or choose the matching agent integration, and deliberately try a real ticket. Keep it useful for both new repositories and already initialized ones; do not modify configuration automatically or add a wizard.

## Acceptance Criteria

- [ ] `chitty guide setup` works outside a repository, names the prerequisites and exact config location, and explains main-checkout versus ticket-worktree changes and how to verify the setup.
- [ ] Dedicated guide tests fail before implementation and pass afterward; `README.md` and `PLAN.md` document the new guide; `make check` passes.

## History

- 2026-11-09T11:51:54Z eager-puffin → todo
