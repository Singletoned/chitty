---
title: Detect a stalled agent session sooner than the 2-hour agent timeout
status: backlog
created: 2026-11-22
---

## Description

Seen 2026-11-22: `chitty run` started a work session on TASK-334 at 10:04; the Pi session file (~/.pi/agent/sessions/...task-334.../2026-11-22T10-05-00\*.jsonl) shows the agent's first tool call (`.venv/bin/chitty show TASK-334`) at 10:05:03 and nothing after. The run log (.git/chitty/run/TASK-334-20261122100400055164Z.log) stayed 0 bytes because `pi -p` prints only at the end. The runner waited the full 7200 s, then set `error` with 'agent timed out after 7200 seconds: (no output)'. The same command returns in under a second by hand, so the stall was in the agent harness. Two hours of the work loop were lost. Idea: an idle timeout (no new commits, worktree changes or log output for N minutes) that ends the session and records the stall distinctly from a real timeout, perhaps retrying once. Needs a design decision on what counts as activity, since `pi -p` gives no output while working.

## Notes

Suggestion origin: chitty

Triage 2026-11-24, from TASK-687 and TASK-657: other stall signs worth detecting. In echonomicon's TASK-203 session (gpt-6-luna), the worker ran `ls`, made two tool calls with an empty command string, then claimed "My available session budget is exhausted." TASK-657 proposes stopping after two consecutive sessions with no non-ticket commit instead of five continuations, and TASK-687 marking the ticket `error` with a pointer to the session logs after N stalled sessions, so it reads as a model problem, not a planning one.

## History

- 2026-11-22T13:57:51Z friendly-jade-stoat → backlog
- 2026-11-22T13:57:51Z friendly-jade-stoat: changed notes
- 2026-11-24T22:39:36Z zesty-coral-newt: changed notes
