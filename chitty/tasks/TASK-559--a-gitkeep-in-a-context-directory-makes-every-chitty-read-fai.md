---
title: A `.gitkeep` in a context directory makes every Chitty read fail
status: backlog
created: 2026-11-22
---

## Description

Repro (2026-11-21, `main` 0.6.x): in a fresh repo run `chitty init`, `chitty add One -d x`, then `touch chitty/tasks/.gitkeep`. `chitty list` now fails with `Error: <root>/chitty/tasks/.gitkeep: task filename '.gitkeep' must end with .md`, committed or not, and `Repo.lookup`/`Repo.tasks` raise the same for every ticket. Placeholder files such as `.gitkeep` are a common way to keep an empty context directory in Git, so one stray file stops all reads. Expected: ignore dot-files (or at least `.gitkeep`) in context and archive directories when listing tickets; `chitty check` could warn about other non-`.md` files instead of every read failing. Found while probing placements for `TASK-393`.

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:33Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:33Z friendly-jade-stoat: changed notes
