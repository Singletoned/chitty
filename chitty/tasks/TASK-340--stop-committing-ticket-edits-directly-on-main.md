---
title: Stop committing ticket edits directly on main
status: backlog
created: 2026-11-16
---

## Description

Planning sessions and the runner commit ticket edits in the main checkout while other agents do the same, which is why amending or rewriting `main` history is unsafe and why concurrent sessions race. The learned rule in `AGENTS.md` already forbids implementation and doc fixes on `main`; ticket edits are the remaining exception. Decide where planning and runner edits go instead (for example a planning worktree or branch per session that lands by fast-forward), so that `main` only moves by fast-forward. Once nothing else commits to `main`, amending a previous Chitty autocommit for the same ticket becomes safe as a further noise reduction.

## History

- 2026-11-16T09:50:22Z intrepid-coral-raven → backlog
