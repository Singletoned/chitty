---
title: Say why the queue is empty when `chitty next` finds no ticket
status: backlog
created: 2026-11-21
---

## Description

Seen 2026-11-20: `chitty run --loop --mode work` kept reporting "no next ticket for --mode work" with 15 `todo` tickets in the queue. The human could not tell why. Every one was skipped. 12 wait (🔗) on tickets still in `planning`: `TASK-378` alone blocks 8 (`TASK-384`, `385`, `386`, `391`, `393`, `394`, `399`, and through them more), and `TASK-353` and `TASK-347` block the rest. The others are ✍️ untestable or 👤 human. Finding this took `chitty list --json` plus reading `skipped`. Suggestion: when nothing is selectable, `chitty next` (and so the runner loop) prints a short summary on stderr after the existing line, for example counts per skip reason and the unfinished blockers ranked by how many tickets they hold up, e.g. "12 waiting: TASK-378 (planning) blocks 8, TASK-353 (planning) blocks 2". Keep the exit code (3) and `--json` unchanged.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:57:52Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:53Z nimble-umber-gannet: changed notes
