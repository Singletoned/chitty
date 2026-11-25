---
title: Give untestable tickets a direct path to done after a human-approved landing
status: backlog
priority: medium
created: 2026-11-25
moved_from: TASK-W8FA7M
---

## Description

Untestable tickets skip work review (docs/plan/pipeline-and-feedback.md), but chitty still requires doing -> review -> done with a note starting 'Reviewed:'. On 2026-11-24 an agent implemented TASK-655 and TASK-642 (both untestable), the person fast-forwarded main, and then the person had to run four commands per ticket, and the first try failed with: 'moving review -> done requires --note starting Reviewed:'. The agent was also blocked by its permission classifier from doing these steps itself, because it looked like self-approval. Possible fix: one command that lands an untestable ticket and records who approved it, or let 'done' accept a 'Landed:' note for untestable tickets.

## Notes

Suggestion origin: chitty

## History

- 2026-11-25T22:28:36Z calm-ochre-quail → backlog
- 2026-11-25T22:28:38Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:30Z calm-ochre-quail: changed priority
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-W8FA7M
