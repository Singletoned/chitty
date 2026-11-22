---
title: Stray untracked files in the main checkout fail landings and stop `run --loop`
status: backlog
created: 2026-11-22
---

## Description

On 2026-11-21, between 08:54 and 09:05, untracked files appeared for a short time in the main checkout. They were not from any ticket branch and were gone by 09:15:

- `tmp-spike378.txt` (probably an interactive spike for TASK-378 that wrote into the main checkout instead of `./tmp/` or a worktree). Landing TASK-426 failed with `Runner error (landing): working tree is dirty ... ?? tmp-spike378.txt` and the ticket went `done → error`, even though its review had passed.
- `chitty/tasks/TASK-3--three.md` (looks like a test fixture written into the real repo instead of a temp dir). The next `chitty run --loop` iteration stopped with exit 1: `Error: TASK-3 is used by more than one file: chitty/tasks/TASK-3--three.md, chitty/tasks/archive/TASK-3--add-a-note-command.md`.

Neither failure was the ticket's fault, but the first left a reviewed ticket that needs a repair agent and the second stopped the whole loop.

Worth deciding:
1. Find what wrote `TASK-3--three.md` into the real `chitty/tasks/`. Search the tests and any spike scripts for a fixture titled "three" whose path is not under a temp dir. A test that escapes its temp dir should fail loudly.
2. Should a landing blocked only by a dirty main checkout leave the ticket `done` and retry on the next run, instead of moving it to `error`? Nothing on the branch needs repair.
3. Should `run --loop` report and wait, instead of exiting, on an error in the main checkout that no ticket owns (a duplicate ID from an untracked file)?

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:34Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:35Z friendly-jade-stoat: changed notes
