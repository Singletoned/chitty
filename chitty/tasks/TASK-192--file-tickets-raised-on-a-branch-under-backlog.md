---
title: File tickets raised on a branch under `BACKLOG`
status: backlog
priority: high
depends_on:
  - TASK-191
parent: TASK-106
created: 2026-11-05
---

## Description

Last of three parts, after `TASK-191`. Make `chitty add` in a linked worktree with no `-c` use the `backlog` context. Put this in `resolve_add_target` in `src/chitty/store.py`, using `git.is_linked_worktree(repo.root)`, so the CLI and `src/chitty/mcp.py` agree. Do not put it in `Repo.add` or `default_context`: `pull` in `src/chitty/inbox.py` calls `repo.add(repo.default_context, ...)` and must keep sequential numbers. An explicit `-c` still wins, as `-c human` needs to. A repository with no `backlog` context, which has not yet run `chitty init`, keeps its default context. Tickets a worker is claiming already exist, so `chitty run` is unaffected.

In `src/chitty/roles/work.md`, `review.md` and `src/chitty/guide.md`, say that unrelated work found on a ticket's branch goes in with plain `chitty add`, which files it as `BACKLOG` for the planning session, and that a person planning should do so from the main checkout, to get normal numbers. Other tickets edit these files, so touch only these bullets. After bumping `__version__`, run `uv run chitty init` and commit `AGENTS.md` and `chitty.toml`. `PLAN.md` records the decision.

## Acceptance Criteria

- [ ] A test with a linked worktree shows plain `chitty add`, through both the CLI and MCP, creating a `BACKLOG-` ticket, `-c human` numbering normally, and inbox pull still numbering normally
- [ ] A test shows `chitty guide work` and `chitty guide review` saying this, `__version__` is bumped above `main`'s, and `PLAN.md` records the decision

## History

- 2026-11-05T14:47:52Z mellow-newt → backlog
