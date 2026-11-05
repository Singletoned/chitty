---
title: File tickets raised on a branch under `BACKLOG`
status: todo
priority: high
depends_on:
  - TASK-191
parent: TASK-106
created: 2026-11-05
---

## Description

Last of three parts, after `TASK-191`. Make `chitty add` in a linked worktree with no `-c` use the `backlog` context. Put this in `resolve_add_target` in `src/chitty/store.py`, using `git.is_linked_worktree(repo.root)`, so the CLI and `src/chitty/mcp.py` agree. Do not put it in `Repo.add` or `default_context`: `pull` in `src/chitty/inbox.py` calls `repo.add(repo.default_context, ...)` and must keep sequential numbers. An explicit `-c` still wins, as `-c human` needs to. A repository with no `backlog` context, which has not yet run `chitty init`, keeps its default context. Tickets a worker is claiming already exist, so `chitty run` is unaffected.

In `src/chitty/roles/work.md`, `review.md` and `src/chitty/guide.md`, say that unrelated work found on a ticket's branch goes in with plain `chitty add`, which files it as `BACKLOG` for the planning session, and that a person planning should do so from the main checkout, to get normal numbers. Other tickets edit these files, so touch only these bullets. After bumping `__version__`, run `uv run chitty init` and commit `AGENTS.md` and `chitty.toml`. From a worktree it prints `skipping machine-wide Pi setup`, which is fine. `PLAN.md` records the decision.

## Acceptance Criteria

- [ ] A test shows `chitty guide work` and `chitty guide review` saying this, `__version__` is bumped above `main`'s, and `PLAN.md` records the decision
- [ ] A test with `git init`, a committed configuration containing `backlog`, and `git worktree add`, run from inside the worktree, shows plain `chitty add T` with no description, through both the CLI and MCP, creating a `BACKLOG-` ticket, `-c human` numbering normally, and inbox pull still numbering normally

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-05. Fixed: the tests' temporary repositories are not Git repositories, so `is_linked_worktree` is false there and the criterion could not be met without saying how to set one up; and no description being needed. It confirmed the check is true for a `chitty run` worktree.

## History

- 2026-11-05T14:47:52Z mellow-newt → backlog
- 2026-11-05T14:50:44Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T14:50:45Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T14:50:47Z mellow-newt backlog → todo
