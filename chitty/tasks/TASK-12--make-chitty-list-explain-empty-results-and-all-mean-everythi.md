---
title: Make chitty list explain empty results, and --all mean everything
status: done
labels:
  - cli
created: 2026-10-26
---

## Description

An empty chitty list prints nothing, so no matches looks like a broken command. --all only adds archived tasks and keeps the todo/doing status default, so it shows nothing when every task is done.

## Acceptance Criteria

- [x] When no task matches, list prints one line to stderr naming the filters in force (statuses, contexts, archived or not); stdout and --json output stay empty
- [x] --all includes every status and both archived and non-archived tasks
- [x] --archived can be combined with -s to filter archived tasks by status
- [x] Tests cover the empty-result message and the new --all meaning
- [x] PLAN.md, README and list --help describe the new behaviour

## Plan

Adjust list selection so --all explicitly selects every status and both locations, preserve --archived with explicit status filters, and emit a concise stderr diagnostic only when the result is empty. Cover CLI output and update command/config documentation.

## Notes

Question: Should an empty JSON list emit the diagnostic? Answer: yes, to stderr only; stdout remains exactly [] for machine readers.

Verified: empty lists explain selected contexts, statuses, and archive scope on stderr while JSON stdout stays []; --all selects all statuses in both locations; --archived retains status filtering. make check passes.
