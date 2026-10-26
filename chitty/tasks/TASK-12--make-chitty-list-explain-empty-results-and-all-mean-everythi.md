---
title: Make chitty list explain empty results, and --all mean everything
status: doing
labels:
  - cli
created: 2026-10-26
---

## Description

An empty chitty list prints nothing, so no matches looks like a broken command. --all only adds archived tasks and keeps the todo/doing status default, so it shows nothing when every task is done.

## Acceptance Criteria

- [ ] When no task matches, list prints one line to stderr naming the filters in force (statuses, contexts, archived or not); stdout and --json output stay empty
- [ ] --all includes every status and both archived and non-archived tasks
- [ ] --archived can be combined with -s to filter archived tasks by status
- [ ] Tests cover the empty-result message and the new --all meaning
- [ ] PLAN.md, README and list --help describe the new behaviour

## Plan

Adjust list selection so --all explicitly selects every status and both locations, preserve --archived with explicit status filters, and emit a concise stderr diagnostic only when the result is empty. Cover CLI output and update command/config documentation.

## Notes

Question: Should an empty JSON list emit the diagnostic? Answer: yes, to stderr only; stdout remains exactly [] for machine readers.
