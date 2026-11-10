---
title: Time out the agent started by chitty run
status: backlog
created: 2026-11-10
---

## Description

A `chitty run --mode work` agent (pi, gpt-6-luna) ran `while ps -p <chitty run pid>; do sleep 5; done`, which waits for its own parent. chitty run waited on the agent, so both hung for about 20 hours with no timeout or warning. Suggest a configurable wall-clock limit on the agent subprocess (plus an idle or no-output limit if feasible). On expiry, kill the agent process group, record the timeout in the ticket history and notes, leave the ticket in a clear state, and move on to the next ticket in `--loop` mode. Possibly also tell agents in the guide not to wait on their parent process.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-10T16:53:45Z jolly-heron → backlog
- 2026-11-10T16:53:45Z jolly-heron: changed notes
