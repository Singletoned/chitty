---
title: Stop `make check` in a worktree from repointing a symlinked `.venv`
status: backlog
created: 2026-11-21
---

## Description

Seen 2026-11-20: an agent made a hand worktree under `.worktrees/` and symlinked `.venv` to the main checkout to skip `make install`. Running `make check` there re-synced the shared venv, so the editable `chitty` in the main `.venv` pointed at the worktree. After the worktree was removed, `.venv/bin/chitty` in main failed with `bad interpreter` until `make install` was rerun in main. A running `chitty run --loop` uses that executable for every attempt. Options: have `make check` refuse when `.venv` is a symlink or when the venv editable install points at another checkout, with a message saying to run `make install` in this worktree; or say in `AGENTS.md` that each worktree needs its own `make install`.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:58:04Z nimble-umber-gannet → backlog
- 2026-11-21T07:58:06Z nimble-umber-gannet: changed notes
