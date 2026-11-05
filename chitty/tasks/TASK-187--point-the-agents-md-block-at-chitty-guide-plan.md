---
title: Point the `AGENTS.md` block at `chitty guide plan`
status: done
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

The block `chitty init` writes into a repository's `AGENTS.md` comes from `src/chitty/guide.md`. It never mentions `chitty guide plan` or cold reads, so an agent writing tickets in another repository only learns that "Backlog tasks need refinement". `src/chitty/roles/plan.md` has the advice, but nothing leads there. `TASK-143` rewrites the whole block and will add such a pointer, but it waits on `TASK-142` and `TASK-144`; this is the one line, sooner.

Directly after the `Backlog tasks need refinement` bullet in `guide.md`, add: "- Writing or refining tickets? Run `chitty guide plan` first: it says how to write them and cold-read them." After bumping `__version__`, run `uv run chitty init` and commit `AGENTS.md` and `chitty.toml`, because `guide.md` reaches `AGENTS.md` only that way. Use `uv run`: a global `chitty` may be another checkout's code, and would write that checkout's guide. `TASK-179` changes the line before, so expect a small conflict. `TASK-143` must keep the pointer, which it already plans to.

## Acceptance Criteria

- [x] A test in `TestGuide` in `tests/test_cli.py` shows `guide()` containing `chitty guide plan`
- [x] `__version__` is bumped above `main`'s, and `AGENTS.md`'s managed block contains `chitty guide plan`

## Plan

1. Update `src/chitty/guide.md` with the `chitty guide plan` pointer immediately after the backlog-refinement bullet.
2. Add a `TestGuide` regression test asserting `guide()` includes the pointer.
3. Bump `src/chitty/__init__.py`, run `uv run chitty init` to refresh the managed `AGENTS.md` block and `chitty.toml`, then run the required checks.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. Serious, fixed: a global `chitty init` in a worktree writes the wrong checkout's guide here. Also, comparing with `chitty guide` gives a false mismatch inside Pi, which adds an actor paragraph, and passed before any work, so the criterion now names the new text.

Implementation will use the repository-local `uv run chitty init` as requested so generated files come from this checkout.

Verified: the new TestGuide regression passes; `AGENTS.md` and `src/chitty/guide.md` contain the pointer; version is 0.1.32 versus main 0.1.31; `make check` passes.

Reviewed: both acceptance criteria pass. The source and regenerated managed guide contain the exact chitty guide plan pointer, version 0.1.32 is above main's 0.1.31, the TestGuide regression is present, and make check plus npm test pass.

## Summary

Implemented and committed in `8430ca2`. Added the `chitty guide plan` pointer to the source guide and regenerated the managed `AGENTS.md`/`chitty.toml` setup at version `0.1.32`; added regression coverage in `TestGuide` and updated the version-sensitive extension test. Verification: `make check` passes (ruff, pyright, 270 unittest tests, and Node tests). No follow-ups.

## History

- 2026-11-05T14:13:55Z mellow-newt → backlog
- 2026-11-05T14:23:14Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T14:23:15Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T14:23:16Z mellow-newt backlog → todo
- 2026-11-05T21:10:23Z quick-toad todo → doing
- 2026-11-05T21:10:44Z quick-toad: changed notes; wrote the plan
- 2026-11-05T21:18:20Z quick-toad: changed notes; ticked acceptance criteria
- 2026-11-05T21:18:29Z quick-toad: changed summary
- 2026-11-05T21:18:29Z quick-toad doing → review
- 2026-11-05T22:12:39Z lively-newt: changed notes
- 2026-11-05T22:12:39Z lively-newt review → done
