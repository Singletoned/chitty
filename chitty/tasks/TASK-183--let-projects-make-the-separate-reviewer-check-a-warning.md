---
title: Let projects make the separate-reviewer check a warning
status: backlog
created: 2026-11-05
---

## Description

A reviewer subagent spawned by a session shares that session`s `chitty` actor, so the self-review guard refuses its write: `Error: youthful-toad cannot review this task: ticked acceptance criteria, moved the task to review`. This happened in `echonomicon` on 2026-11-05 on `TASK-29`, even though the review ran in a fresh context with a different model. The only way through is setting `CHITTY_ACTOR` to an invented name, which makes the history less truthful and teaches agents to bypass the guard. Requested by the project owner: a `chitty.toml` option to turn enforcement of separate reviewers off, so that it warns instead of refuses. The warning should still appear and the history should still record the same actor, so a same-actor review stays visible. Related: consider giving subagents a distinct actor automatically.

## Notes

Suggestion origin: echonomicon

Archived in backlog triage (human approved, 2026-11-11): merged into TASK-209.

## History

- 2026-11-05T11:05:03Z able-yellowhammer → backlog
- 2026-11-05T11:05:03Z able-yellowhammer: changed notes
- 2026-11-11T10:18:41Z vivid-yellowhammer: changed notes
