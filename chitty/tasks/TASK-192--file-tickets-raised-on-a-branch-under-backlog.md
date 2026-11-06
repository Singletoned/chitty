---
title: File tickets raised on a branch under `BACKLOG`
status: done
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

- [x] A test shows `chitty guide work` and `chitty guide review` saying this, `__version__` is bumped above `main`'s, and `PLAN.md` records the decision
- [x] A test with `git init`, a committed configuration containing `backlog`, and `git worktree add`, run from inside the worktree, shows plain `chitty add T` with no description, through both the CLI and MCP, creating a `BACKLOG-` ticket, `-c human` numbering normally, and inbox pull still numbering normally

## Plan

1. Update `resolve_add_target` to select the configured `backlog` context for plain adds from linked worktrees, while preserving explicit contexts, missing-backlog fallback, and normal inbox behavior.
2. Add regression coverage using real Git repositories/worktrees for CLI and MCP, including explicit `human` and inbox numbering.
3. Update the narrowly scoped work/review/general guide bullets and the relevant `PLAN.md` decision, bump `__version__`, run `chitty init`, and commit generated guide/config changes.
4. Run formatting and the complete `make check`, then record verification.

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-05. Fixed: the tests' temporary repositories are not Git repositories, so `is_linked_worktree` is false there and the criterion could not be met without saying how to set one up; and no description being needed. It confirmed the check is true for a `chitty run` worktree.

Regression coverage initially failed without the fix: plain CLI add in a linked worktree required --description; after the fix, CLI, MCP, guide, and inbox tests pass. chitty fix reported only pre-existing ticket Markdown warnings.

Review failed (work): the branch changes `chitty.toml`; only `chitty init` on the main checkout may change it.

Review follow-up: restored chitty.toml to the main-branch version; the ticket branch retains only the source version bump, while generated config upgrades remain a main-checkout operation. make format and make check pass (341 Python tests and Node tests). chitty fix was run and reported the known unresolved repository setup warning.

Reviewed: independently inspected the implementation, guidance, PLAN.md, tests, and diff. make format and make check pass (341 Python tests, pyright, ruff, and Node tests).
1: pass - Guide text, version bump, and PLAN.md decision are present and tested.
2: pass - Linked-worktree CLI/MCP routing, explicit human numbering, and inbox default numbering are covered and passing.

## Summary

Implemented linked-worktree add routing in resolve_add_target, preserving explicit contexts, missing-backlog fallback, and inbox sequential numbering. Added real Git worktree coverage for CLI/MCP, guide coverage, inbox regression coverage, and updated the planning/guidance text. Source version is 0.1.37; chitty.toml remains at the main-branch version per review guidance. Verified with make format and make check (341 Python tests, pyright, ruff, and Node tests). Follow-up: generated config upgrades belong on the main checkout.

## History

- 2026-11-05T14:47:52Z mellow-newt → backlog
- 2026-11-05T14:50:44Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T14:50:45Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T14:50:47Z mellow-newt backlog → todo
- 2026-11-06T19:31:50Z golden-lapwing todo → doing
- 2026-11-06T19:32:17Z golden-lapwing: wrote the plan
- 2026-11-06T19:59:09Z golden-lapwing: changed notes, summary; ticked acceptance criteria
- 2026-11-06T19:59:09Z golden-lapwing doing → review
- 2026-11-06T19:59:51Z golden-quail: changed notes
- 2026-11-06T19:59:51Z golden-quail review → doing
- 2026-11-06T20:02:15Z quick-raven: changed notes, summary; ticked acceptance criteria
- 2026-11-06T20:02:15Z quick-raven doing → review
- 2026-11-06T20:05:01Z quick-lapwing: changed notes; ticked acceptance criteria
- 2026-11-06T20:05:01Z quick-lapwing review → done
