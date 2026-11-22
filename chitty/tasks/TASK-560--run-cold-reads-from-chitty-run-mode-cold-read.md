---
title: Run cold reads from `chitty run --mode cold-read`
status: backlog
labels:
  - duplicate
created: 2026-11-22
---

## Description

Today a planner starts each cold read by hand (Claude Code planners use the `cold-reader` subagent, `.claude/agents/cold-reader.md`, model Haiku) and waits for its report; the report lives only in the planner's conversation, and only the planner's summary of outcomes reaches the ticket. On 2026-11-21 a planning session ran four reads this way, one ticket at a time, blocking on each.

Suggestion: a runner mode `cold-read`. It picks a ticket in `cold-read`, runs the reader with the configured agent command (so the reader is a cheap model close to the worker, as `docs/plan/pipeline-and-feedback.md` asks), with the prompt from `chitty guide cold-read <ID>`. It saves the report to a file, not a ticket note (command output never goes into tickets; for example `.chitty/cold-read/<ID>.md` in the main checkout, ignored through Git's exclude file as the run log is), then moves the ticket to `planning` with a one-line note naming the report. The planner keeps the judgement step: it settles each finding and promotes the ticket. The reader never moves a ticket to `todo`.

Depends on the read-only mode suggestion ("Add a read-only mode that refuses every Chitty write", 2026-11-21): the runner sets `CHITTY_READ_ONLY=1` for the reader, because an unattended reader is where a stray write (112 tickets moved by a reader on 2026-11-21) would go unnoticed.

Open questions for planning: how a planner learns a report is ready (`chitty next --mode plan`?); whether to feed planners one ticket at a time, since the planning guide warns that fixes written for several tickets at once drift from the code; and whether the Claude Code subagent remains as a fallback.

## Notes

Suggestion origin: chitty

Planner, 2026-11-22: overlaps `TASK-259`, `TASK-272` and `TASK-274` (cold reads through `chitty run`). This one adds the report file and the read-only dependency (`TASK-558`); fold those into the earliest of them when it is planned.

## History

- 2026-11-22T09:47:33Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:34Z friendly-jade-stoat: changed notes
- 2026-11-22T09:51:01Z friendly-jade-stoat: changed labels, notes
