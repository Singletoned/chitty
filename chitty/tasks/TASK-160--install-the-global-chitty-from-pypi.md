---
title: Install the global `chitty` from PyPI
status: backlog
priority: medium
owner: human
depends_on:
  - TASK-80
parent: TASK-106
created: 2026-11-04
---

## Description

The human decided on 2026-11-04 that the global `chitty` is the latest PyPI release, not an editable install of `main`. That needs a release first: PyPI has 0.1.19, which is believed to have no `chitty run`, and `main` has many unpushed commits.

Once `main` is ready, in this order, in the human's shell and with the planning session writing the documentation:

1. `make release`, which is the first real push and publish.
2. `uv tool install --force 'chitty[mcp]'`, once PyPI has it.
3. Run `make install` in the main checkout. Add `PATH_add .venv/bin` to the local, ignored `.envrc`, and correct its comment, which forbids setting `PATH`: the danger it describes comes from `uv` variables, and adding to `PATH` does not repoint a `uv` environment. In this repository `main` is usually ahead of PyPI, so the global `chitty` would refuse writes with `repository needs Chitty X or later`. Worktrees inherit this, so a person there runs `main`'s code, as today; agents already use their worktree's own through `uv run`.
4. Delete `~/.envs/chitty`, and remove its activation if it has one, which the human is doing as part of retiring `~/.envs`.

`README.md` replaces the editable install section with this.

## Acceptance Criteria

- [ ] `chitty --version` outside this repository reports the PyPI release from a non-editable install, and in the main checkout `chitty next` works when `main` is ahead of it
- [ ] `README.md` describes installing from PyPI, and using `.venv` when developing Chitty

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: a stale count, the `.envrc` comment, which did forbid `PATH`, and `make install` first. `TASK-122` assumes the editable global this reverses, so it is archived. Rejected: a criterion for deleting `~/.envs/chitty`, which is the human's own clean-up; and a repeatable test of `.envrc`, which is local to this machine.

## History

- 2026-11-04T19:32:39Z mellow-newt → backlog
- 2026-11-04T19:36:40Z mellow-newt: changed description, notes
