---
title: Worker deadlocks waiting on its own `chitty run` parent process
status: backlog
created: 2026-11-10
---

## Description

Seen in mullion TASK-2 on 2026-11-09. Mullion is a Chitty project, and its `chitty run --mode work` loop was using model `gpt-6-luna`.

What happened: the worker started under `chitty run` (process 25131) and ran `chitty show TASK-2`. The output contained `running: work by lively-adder, process 25131, since 20:43`. The worker took that for a different worker, refused to touch the files, and ran `while ps -p 25131 >/dev/null; do sleep 5; done`. That loop waits on its own parent, so it can never end. The ticket sat in `doing` for about 20 hours. An earlier worker on the same ticket had polled its own parent the same way (`ps -p 4116`) before giving up.

Suggested fixes:
1. When `chitty show` runs inside the session that holds the run lock (detect it from the parent process or an env var that `chitty run` sets), print something like `running: this session` or leave the line out. That way a worker cannot read itself as a rival.
2. The bash call had `timeout: 300000` but never returned, and the session log just stops. Check whether Pi enforces the timeout on the bash tool, or whether `chitty run` should have a wall-clock limit per agent run and kill the agent when it is exceeded.

Related: before that, two workers moved TASK-2 to `review` with all of the implementation left untracked in `tests/harness/`, even though the work guide says `git status --short` must be empty first. Both reviews failed on uncommitted changes. `chitty edit -s review` could refuse while the worktree is dirty, so this is caught at handoff and the review cycle is not wasted.

## Notes

Suggestion origin: mullion

## History

- 2026-11-10T19:32:32Z jolly-heron → backlog
- 2026-11-10T19:32:33Z jolly-heron: changed notes
