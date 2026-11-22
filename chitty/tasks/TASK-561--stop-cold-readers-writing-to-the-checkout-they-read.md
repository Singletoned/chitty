---
title: Stop cold readers writing to the checkout they read
status: backlog
created: 2026-11-22
---

## Description

On 2026-11-21 a cold-reader subagent (`.claude/agents/cold-reader`, Haiku), reading `TASK-367` which mentions `chitty archive` with no ID, ran `chitty archive` in the main checkout to probe it. It moved 112 done tickets into `chitty/tasks/archive/` without committing before the agent killed it and restored them by hand (`git status` clean afterwards). The cold-read guide says to report without changing the checkout, but nothing enforces it and a reader probing commands naturally runs them where it stands. Ideas: the cold-read guide tells readers to try commands only in a fresh `git init` repository under a temporary directory; or the cold-reader agent runs with an env var that makes Chitty refuse every write (for example `CHITTY_READ_ONLY=1`). Also worth checking separately: `chitty archive` with no ID took long enough to be killed mid-run after moving 112 files with nothing committed, so a killed archive leaves the checkout half-moved.

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:34Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:34Z friendly-jade-stoat: changed notes
